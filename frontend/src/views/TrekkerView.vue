<template>
  <div style="background:#f5f0eb; min-height:100vh;">

    <!-- Navbar -->
    <nav class="navbar px-4 py-3" style="background:#4a6741;">
      <span class="navbar-brand text-white fw-bold">Trekking Management Portal</span>
      <span class="text-white me-3" style="font-size:0.9rem;">Hi, {{ user?.full_name }}</span>
      <button @click="handleLogout" class="btn btn-sm" style="background:#c8b89a; color:#3a2a1a;">Logout</button>
    </nav>

    <div class="container py-4">

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item" v-for="tab in tabs" :key="tab">
          <a class="nav-link" :class="{ active: activeTab === tab }"
            @click="activeTab = tab" href="#"
            style="color:#4a6741;">{{ tab }}</a>
        </li>
      </ul>

      <!-- BROWSE TREKS TAB -->
      <div v-if="activeTab === 'Browse Treks'">
        <h5 class="mb-3" style="color:#5a4a3a;">Available Treks</h5>

        <!-- Filters -->
        <div class="row g-2 mb-3">
          <div class="col-md-4">
            <input v-model="search" @input="loadTreks"
              class="form-control form-control-sm" placeholder="🔍 Search by name or location" />
          </div>
          <div class="col-md-3">
            <select v-model="filterDifficulty" @change="loadTreks" class="form-select form-select-sm">
              <option value="">All Difficulties</option>
              <option>Easy</option>
              <option>Moderate</option>
              <option>Hard</option>
            </select>
          </div>
          <div class="col-md-3">
            <input v-model="filterLocation" @input="loadTreks"
              class="form-control form-control-sm" placeholder="Filter by location" />
          </div>
          <div class="col-md-2">
            <button @click="clearFilters" class="btn btn-sm w-100"
              style="background:#c8b89a; color:#3a2a1a;">Clear</button>
          </div>
        </div>

        <!-- Trek Cards -->
        <div class="row g-3">
          <div class="col-md-4" v-for="trek in treks" :key="trek.id">
            <div class="card h-100 p-3" style="border:1px solid #c8b89a;">
              <h6 style="color:#4a6741;">{{ trek.name }}</h6>
              <p class="text-muted mb-1" style="font-size:0.85rem;"> {{ trek.location }}</p>
              <p class="text-muted mb-1" style="font-size:0.85rem;"> {{ trek.difficulty }}</p>
              <p class="text-muted mb-1" style="font-size:0.85rem;"> {{ trek.duration_days }} days</p>
              <p class="text-muted mb-1" style="font-size:0.85rem;"> {{ trek.available_slots }} slots left</p>
              <p class="text-muted mb-2" style="font-size:0.85rem;">
                {{ trek.start_date }} → {{ trek.end_date }}
              </p>
              <p class="text-muted mb-3" style="font-size:0.82rem;">{{ trek.description }}</p>
              <button @click="bookTrek(trek.id)" class="btn btn-sm mt-auto"
                style="background:#4a6741; color:white;"
                :disabled="trek.available_slots === 0">
                {{ trek.available_slots === 0 ? 'Full' : 'Book Now' }}
              </button>
              <p v-if="bookMsg[trek.id]" class="mt-2 mb-0 text-success" style="font-size:0.82rem;">
                {{ bookMsg[trek.id] }}
              </p>
            </div>
          </div>
          <div v-if="treks.length === 0" class="text-muted">
            No open treks available right now.
          </div>
        </div>
      </div>

      <!-- MY BOOKINGS TAB -->
      <div v-if="activeTab === 'My Bookings'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 style="color:#5a4a3a;">My Bookings</h5>
          <button @click="exportCSV" class="btn btn-sm"
            style="background:#c8b89a; color:#3a2a1a;">
            Export CSV 
          </button>
        </div>

        <div v-if="exportMsg" class="alert alert-success py-2 mb-3" style="font-size:0.85rem;">
          {{ exportMsg }}
        </div>

        <!-- Filter by status -->
        <select v-model="bookingFilter" @change="loadBookings"
          class="form-select form-select-sm mb-3" style="width:200px;">
          <option value="">All Bookings</option>
          <option value="Booked">Active</option>
          <option value="Cancelled">Cancelled</option>
          <option value="Completed">Completed</option>
        </select>

        <div class="table-responsive">
          <table class="table table-hover" style="font-size:0.9rem;">
            <thead style="background:#e8ddd0;">
              <tr>
                <th>Trek</th><th>Location</th><th>Dates</th>
                <th>Booked On</th><th>Status</th><th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td>{{ b.trek_name }}</td>
                <td>{{ b.trek_location }}</td>
                <td style="font-size:0.82rem;">{{ b.start_date }} → {{ b.end_date }}</td>
                <td>{{ b.booking_date?.slice(0,10) }}</td>
                <td>
                  <span class="badge" :style="statusBadge(b.status)">{{ b.status }}</span>
                </td>
                <td>
                  <button v-if="b.status === 'Booked'"
                    @click="cancelBooking(b.id)"
                    class="btn btn-sm btn-outline-danger">
                    Cancel
                  </button>
                  <span v-else class="text-muted" style="font-size:0.82rem;">—</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="bookings.length === 0" class="text-muted">No bookings found.</p>
        </div>
      </div>

      <!-- PROFILE TAB -->
      <div v-if="activeTab === 'Profile'">
        <h5 class="mb-3" style="color:#5a4a3a;">My Profile</h5>
        <div class="card p-4" style="max-width:450px; border:1px solid #c8b89a;">
          <div class="mb-3">
            <label class="form-label fw-semibold" style="color:#5a4a3a;">Full Name</label>
            <input v-model="profile.full_name" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold" style="color:#5a4a3a;">Email</label>
            <input :value="profile.email" class="form-control" disabled />
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold" style="color:#5a4a3a;">Username</label>
            <input :value="profile.username" class="form-control" disabled />
          </div>
          <div class="mb-4">
            <label class="form-label fw-semibold" style="color:#5a4a3a;">Phone</label>
            <input v-model="profile.phone" class="form-control" />
          </div>
          <button @click="updateProfile" class="btn"
            style="background:#4a6741; color:white;">
            Save Changes
          </button>
          <p v-if="profileMsg" class="mt-2 text-success mb-0" style="font-size:0.85rem;">
            {{ profileMsg }}
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router  = useRouter()
const auth    = useAuthStore()
const user    = auth.user
const activeTab = ref('Browse Treks')
const tabs    = ['Browse Treks', 'My Bookings', 'Profile']

const treks          = ref([])
const bookings       = ref([])
const bookMsg        = ref({})
const bookingFilter  = ref('')
const search         = ref('')
const filterDifficulty = ref('')
const filterLocation = ref('')
const exportMsg      = ref('')
const profileMsg     = ref('')
const profile        = ref({ full_name:'', email:'', username:'', phone:'' })

function statusBadge(status) {
  const colors = {
    Booked:    'background:#4a6741',
    Cancelled: 'background:#a05c3a',
    Completed: 'background:#3a5a7a',
  }
  return (colors[status] || 'background:#888') + '; color:white'
}

async function loadTreks() {
  const params = {}
  if (search.value)          params.search     = search.value
  if (filterDifficulty.value) params.difficulty = filterDifficulty.value
  if (filterLocation.value)  params.location   = filterLocation.value
  const res  = await api.get('/user/treks', { params })
  treks.value = res.data.treks
}

async function bookTrek(trekId) {
  try {
    await api.post(`/user/treks/${trekId}/book`)
    bookMsg.value[trekId] = '✓ Booked successfully!'
    await loadTreks()
    setTimeout(() => bookMsg.value[trekId] = '', 3000)
  } catch (e) {
    bookMsg.value[trekId] = e.response?.data?.message || 'Error'
    setTimeout(() => bookMsg.value[trekId] = '', 3000)
  }
}

async function loadBookings() {
  const params = {}
  if (bookingFilter.value) params.status = bookingFilter.value
  const res    = await api.get('/bookings/my-history', { params })
  bookings.value = res.data.bookings
}

async function cancelBooking(bookingId) {
  if (!confirm('Cancel this booking?')) return
  await api.post(`/user/bookings/${bookingId}/cancel`)
  await loadBookings()
  await loadTreks()
}

async function exportCSV() {
  try {
    await api.post('/jobs/export-csv')
    exportMsg.value = 'Export started! You will receive an email shortly.'
    setTimeout(() => exportMsg.value = '', 5000)
  } catch (e) {
    exportMsg.value = 'Export failed'
  }
}

async function loadProfile() {
  const res    = await api.get('/user/profile')
  profile.value = res.data
}

async function updateProfile() {
  await api.put('/user/profile', {
    full_name: profile.value.full_name,
    phone:     profile.value.phone,
  })
  profileMsg.value = '✓ Profile updated!'
  setTimeout(() => profileMsg.value = '', 3000)
}

function clearFilters() {
  search.value          = ''
  filterDifficulty.value = ''
  filterLocation.value  = ''
  loadTreks()
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(async () => {
  await loadTreks()
  await loadBookings()
  await loadProfile()
})
</script>