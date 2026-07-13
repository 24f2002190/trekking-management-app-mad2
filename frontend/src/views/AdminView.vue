<template>
  <div style="background:#f5f0eb; min-height:100vh;">

    <!-- Navbar -->
    <nav class="navbar px-4 py-3" style="background:#4a6741;">
      <span class="navbar-brand text-white fw-bold">Trekking Portal - Admin</span>
      <button @click="handleLogout" class="btn btn-sm" style="background:#c8b89a; color:#3a2a1a;">Logout</button>
    </nav>

    <div class="container py-4">

      <!-- Stats Row -->
      <div class="row g-3 mb-4">
        <div class="col-md-3" v-for="stat in stats" :key="stat.label">
          <div class="card text-center p-3" style="border:1px solid #c8b89a;">
            <h3 style="color:#4a6741;">{{ stat.value }}</h3>
            <p class="mb-0 text-muted" style="font-size:0.85rem;">{{ stat.label }}</p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item" v-for="tab in tabs" :key="tab">
          <a class="nav-link" :class="{ active: activeTab === tab }"
            @click="activeTab = tab" href="#"
            style="color:#4a6741;">{{ tab }}</a>
        </li>
      </ul>

      <!-- TREKS TAB -->
      <div v-if="activeTab === 'Treks'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 style="color:#5a4a3a;">All Treks</h5>
          <button class="btn btn-sm" style="background:#4a6741; color:white;"
            @click="showTrekForm = !showTrekForm">
            + New Trek
          </button>
        </div>

        <!-- Create Trek Form -->
        <div v-if="showTrekForm" class="card p-3 mb-3" style="border:1px solid #c8b89a;">
          <h6 style="color:#5a4a3a;">Create New Trek</h6>
          <div class="row g-2">
            <div class="col-md-6">
              <input v-model="newTrek.name" class="form-control form-control-sm" placeholder="Trek Name" />
            </div>
            <div class="col-md-6">
              <input v-model="newTrek.location" class="form-control form-control-sm" placeholder="Location" />
            </div>
            <div class="col-md-4">
              <select v-model="newTrek.difficulty" class="form-select form-select-sm">
                <option value="">Difficulty</option>
                <option>Easy</option>
                <option>Moderate</option>
                <option>Hard</option>
              </select>
            </div>
            <div class="col-md-4">
              <input v-model="newTrek.duration_days" type="number" class="form-control form-control-sm" placeholder="Duration (days)" />
            </div>
            <div class="col-md-4">
              <input v-model="newTrek.total_slots" type="number" class="form-control form-control-sm" placeholder="Total Slots" />
            </div>
            <div class="col-md-6">
              <input v-model="newTrek.start_date" type="date" class="form-control form-control-sm" />
            </div>
            <div class="col-md-6">
              <input v-model="newTrek.end_date" type="date" class="form-control form-control-sm" />
            </div>
            <div class="col-12">
              <textarea v-model="newTrek.description" class="form-control form-control-sm" placeholder="Description" rows="2"></textarea>
            </div>
            <div class="col-12">
              <button @click="createTrek" class="btn btn-sm" style="background:#4a6741; color:white;">
                Create Trek
              </button>
              <span v-if="trekMsg" class="ms-3 text-success" style="font-size:0.85rem;">{{ trekMsg }}</span>
            </div>
          </div>
        </div>

        <!-- Trek Table -->
        <div class="table-responsive">
          <table class="table table-hover" style="font-size:0.9rem;">
            <thead style="background:#e8ddd0;">
              <tr>
                <th>Name</th><th>Location</th><th>Difficulty</th>
                <th>Slots</th><th>Status</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trek in treks" :key="trek.id">
                <td>{{ trek.name }}</td>
                <td>{{ trek.location }}</td>
                <td>{{ trek.difficulty }}</td>
                <td>{{ trek.available_slots }}/{{ trek.total_slots }}</td>
                <td>
                  <span class="badge" :style="statusBadge(trek.status)">{{ trek.status }}</span>
                </td>
                <td>
                  <select class="form-select form-select-sm d-inline w-auto me-1"
                    @change="updateTrekStatus(trek.id, $event.target.value)">
                    <option value="">Change Status</option>
                    <option>Pending</option>
                    <option>Approved</option>
                    <option>Open</option>
                    <option>Closed</option>
                    <option>Completed</option>
                  </select>
                  <button @click="deleteTrek(trek.id)" class="btn btn-sm btn-outline-danger">🗑</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- STAFF TAB -->
      <div v-if="activeTab === 'Staff'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 style="color:#5a4a3a;">Trek Staff</h5>
          <button class="btn btn-sm" style="background:#4a6741; color:white;"
            @click="showStaffForm = !showStaffForm">
            + Add Staff
          </button>
        </div>

        <!-- Add Staff Form -->
        <div v-if="showStaffForm" class="card p-3 mb-3" style="border:1px solid #c8b89a;">
          <h6 style="color:#5a4a3a;">Add New Staff Member</h6>
          <div class="row g-2">
            <div class="col-md-6">
              <input v-model="newStaff.full_name" class="form-control form-control-sm" placeholder="Full Name" />
            </div>
            <div class="col-md-6">
              <input v-model="newStaff.username" class="form-control form-control-sm" placeholder="Username" />
            </div>
            <div class="col-md-6">
              <input v-model="newStaff.email" class="form-control form-control-sm" placeholder="Email" />
            </div>
            <div class="col-md-6">
              <input v-model="newStaff.password" type="password" class="form-control form-control-sm" placeholder="Password" />
            </div>
            <div class="col-md-6">
              <input v-model="newStaff.contact_detail" class="form-control form-control-sm" placeholder="Contact" />
            </div>
            <div class="col-12">
              <button @click="createStaff" class="btn btn-sm" style="background:#4a6741; color:white;">
                Add Staff
              </button>
              <span v-if="staffMsg" class="ms-3 text-success" style="font-size:0.85rem;">{{ staffMsg }}</span>
            </div>
          </div>
        </div>

        <!-- Staff Table -->
        <div class="table-responsive">
          <table class="table table-hover" style="font-size:0.9rem;">
            <thead style="background:#e8ddd0;">
              <tr>
                <th>Name</th><th>Email</th><th>Contact</th><th>Assigned Treks</th><th>Assign Trek</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in staffList" :key="s.id">
                <td>{{ s.name }}</td>
                <td>{{ s.email }}</td>
                <td>{{ s.contact_detail }}</td>
                <td>{{ s.assigned_treks.map(t => t.name).join(', ') || '—' }}</td>
                <td>
                  <select class="form-select form-select-sm d-inline w-auto"
                    @change="assignStaff(s.id, $event.target.value)">
                    <option value="">Assign to Trek</option>
                    <option v-for="t in treks" :key="t.id" :value="t.id">{{ t.name }}</option>
                  </select>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- USERS TAB -->
      <div v-if="activeTab === 'Users'">
        <h5 class="mb-3" style="color:#5a4a3a;">Registered Trekkers</h5>
        <div class="table-responsive">
          <table class="table table-hover" style="font-size:0.9rem;">
            <thead style="background:#e8ddd0;">
              <tr><th>Name</th><th>Email</th><th>Username</th><th>Status</th><th>Action</th></tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.full_name }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.username }}</td>
                <td>
                  <span class="badge" :style="u.active ? 'background:#4a6741' : 'background:#a05c3a'">
                    {{ u.active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <button v-if="u.active" @click="deactivateUser(u.id)"
                    class="btn btn-sm btn-outline-danger">Deactivate</button>
                  <button v-else @click="activateUser(u.id)"
                    class="btn btn-sm btn-outline-success">Activate</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- BOOKINGS TAB -->
      <div v-if="activeTab === 'Bookings'">
        <h5 class="mb-3" style="color:#5a4a3a;">All Bookings</h5>
        <div class="table-responsive">
          <table class="table table-hover" style="font-size:0.9rem;">
            <thead style="background:#e8ddd0;">
              <tr><th>User</th><th>Trek</th><th>Booked On</th><th>Status</th><th>Payment</th></tr>
            </thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td>{{ b.user }}</td>
                <td>{{ b.trek }}</td>
                <td>{{ b.booking_date?.slice(0,10) }}</td>
                <td><span class="badge" :style="statusBadge(b.status)">{{ b.status }}</span></td>
                <td>{{ b.payment_status }}</td>
              </tr>
            </tbody>
          </table>
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

const router      = useRouter()
const auth        = useAuthStore()
const activeTab   = ref('Treks')
const tabs        = ['Treks', 'Staff', 'Users', 'Bookings']
const showTrekForm  = ref(false)
const showStaffForm = ref(false)
const trekMsg     = ref('')
const staffMsg    = ref('')

const stats     = ref([])
const treks     = ref([])
const staffList = ref([])
const users     = ref([])
const bookings  = ref([])

const newTrek = ref({
  name:'', location:'', difficulty:'', duration_days:'',
  total_slots:'', start_date:'', end_date:'', description:''
})

const newStaff = ref({
  full_name:'', username:'', email:'', password:'', contact_detail:''
})

function statusBadge(status) {
  const colors = {
    Open:      'background:#4a6741',
    Closed:    'background:#a05c3a',
    Pending:   'background:#8a7a5a',
    Completed: 'background:#3a5a7a',
    Booked:    'background:#4a6741',
    Cancelled: 'background:#a05c3a',
  }
  return (colors[status] || 'background:#888') + '; color:white'
}

async function loadDashboard() {
  const res = await api.get('/admin/dashboard')
  const d   = res.data
  stats.value = [
    { label: 'Total Treks',    value: d.total_treks },
    { label: 'Total Bookings', value: d.total_bookings },
    { label: 'Staff Members',  value: d.total_staff },
    { label: 'Trekkers',       value: d.total_trekkers },
  ]
}

async function loadTreks() {
  const res  = await api.get('/admin/treks')
  treks.value = res.data.treks
}

async function loadStaff() {
  const res      = await api.get('/admin/staff')
  staffList.value = res.data.staff
}

async function loadUsers() {
  const res   = await api.get('/admin/users')
  users.value = res.data.users
}

async function loadBookings() {
  const res      = await api.get('/admin/bookings')
  bookings.value = res.data.bookings
}

async function createTrek() {
  try {
    await api.post('/admin/treks', {
      ...newTrek.value,
      duration_days: parseInt(newTrek.value.duration_days),
      total_slots:   parseInt(newTrek.value.total_slots),
    })
    trekMsg.value = 'Trek created!'
    showTrekForm.value = false
    await loadTreks()
    await loadDashboard()
    setTimeout(() => trekMsg.value = '', 3000)
  } catch (e) {
    trekMsg.value = e.response?.data?.message || 'Error'
  }
}

async function updateTrekStatus(trekId, status) {
  if (!status) return
  await api.put(`/admin/treks/${trekId}`, { status })
  await loadTreks()
}

async function deleteTrek(trekId) {
  if (!confirm('Delete this trek?')) return
  await api.delete(`/admin/treks/${trekId}`)
  await loadTreks()
  await loadDashboard()
}

async function createStaff() {
  try {
    await api.post('/admin/staff', newStaff.value)
    staffMsg.value = 'Staff added!'
    showStaffForm.value = false
    await loadStaff()
    await loadDashboard()
    setTimeout(() => staffMsg.value = '', 3000)
  } catch (e) {
    staffMsg.value = e.response?.data?.message || 'Error'
  }
}

async function assignStaff(staffId, trekId) {
  if (!trekId) return
  await api.post(`/admin/staff/${staffId}/assign/${trekId}`)
  await loadStaff()
}

async function deactivateUser(userId) {
  await api.post(`/admin/users/${userId}/deactivate`)
  await loadUsers()
}

async function activateUser(userId) {
  await api.post(`/admin/users/${userId}/activate`)
  await loadUsers()
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(async () => {
  await loadDashboard()
  await loadTreks()
  await loadStaff()
  await loadUsers()
  await loadBookings()
})
</script>