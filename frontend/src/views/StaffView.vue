<template>
  <div style="background:#f5f0eb; min-height:100vh;">

    <!-- Navbar -->
    <nav class="navbar px-4 py-3" style="background:#4a6741;">
      <span class="navbar-brand text-white fw-bold">Trekking Portal - Staff</span>
      <span class="text-white me-3" style="font-size:0.9rem;">{{ staffName }}</span>
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

      <!-- DASHBOARD TAB -->
      <div v-if="activeTab === 'Dashboard'">
        <h5 class="mb-3" style="color:#5a4a3a;">My Assigned Treks</h5>
        <div class="row g-3">
          <div class="col-md-4" v-for="trek in assignedTreks" :key="trek.id">
            <div class="card p-3" style="border:1px solid #c8b89a;">
              <h6 style="color:#4a6741;">{{ trek.name }}</h6>
              <p class="mb-1 text-muted" style="font-size:0.85rem;">📍 {{ trek.location }}</p>
              <p class="mb-1 text-muted" style="font-size:0.85rem;">🧗 {{ trek.difficulty }}</p>
              <p class="mb-1 text-muted" style="font-size:0.85rem;">🎫 {{ trek.available_slots }}/{{ trek.total_slots }} slots</p>
              <span class="badge" :style="statusBadge(trek.status)">{{ trek.status }}</span>
              <p class="mt-2 mb-0" style="font-size:0.85rem; color:#4a6741;">
                👥 {{ trek.registered_trekkers }} trekkers registered
              </p>
            </div>
          </div>
          <div v-if="assignedTreks.length === 0" class="text-muted">
            No treks assigned to you yet.
          </div>
        </div>
      </div>

      <!-- MANAGE TREKS TAB -->
      <div v-if="activeTab === 'Manage Treks'">
        <h5 class="mb-3" style="color:#5a4a3a;">Update Trek Details</h5>
        <div class="card p-3 mb-3" v-for="trek in assignedTreks" :key="trek.id"
          style="border:1px solid #c8b89a;">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 style="color:#4a6741;">{{ trek.name }}</h6>
              <p class="mb-1 text-muted" style="font-size:0.85rem;">{{ trek.location }} · {{ trek.difficulty }}</p>
              <span class="badge" :style="statusBadge(trek.status)">{{ trek.status }}</span>
            </div>
            <div class="d-flex gap-2 align-items-center">
              <!-- Update slots -->
              <input type="number" class="form-control form-control-sm" style="width:100px;"
                :value="trek.available_slots"
                :ref="el => slotInputs[trek.id] = el"
                placeholder="Slots" />

              <!-- Update status -->
              <select class="form-select form-select-sm" style="width:130px;"
                :ref="el => statusSelects[trek.id] = el">
                <option value="">Status</option>
                <option>Open</option>
                <option>Closed</option>
                <option>Ongoing</option>
                <option>Completed</option>
              </select>

              <button @click="updateTrek(trek.id)" class="btn btn-sm"
                style="background:#4a6741; color:white;">
                Update
              </button>
            </div>
          </div>

          <div v-if="updateMsg[trek.id]" class="mt-2 text-success" style="font-size:0.85rem;">
            {{ updateMsg[trek.id] }}
          </div>

          <!-- Quick actions -->
          <div class="mt-2 d-flex gap-2">
            <button @click="markStarted(trek.id)" class="btn btn-sm btn-outline-secondary">
              Mark Started
            </button>
            <button @click="markCompleted(trek.id)" class="btn btn-sm btn-outline-secondary">
              Mark Completed
            </button>
          </div>
        </div>
      </div>

      <!-- PARTICIPANTS TAB -->
      <div v-if="activeTab === 'Participants'">
        <h5 class="mb-3" style="color:#5a4a3a;">Trek Participants</h5>

        <!-- Trek selector -->
        <select v-model="selectedTrekId" class="form-select mb-3" style="width:250px;"
          @change="loadParticipants">
          <option value="">Select a trek</option>
          <option v-for="t in assignedTreks" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>

        <div v-if="participants.length > 0">
          <p class="text-muted mb-2" style="font-size:0.85rem;">
            {{ participants.length }} participant(s) registered
          </p>
          <div class="table-responsive">
            <table class="table table-hover" style="font-size:0.9rem;">
              <thead style="background:#e8ddd0;">
                <tr>
                  <th>Name</th><th>Email</th><th>Booked On</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in participants" :key="p.booking_id">
                  <td>{{ p.name }}</td>
                  <td>{{ p.email }}</td>
                  <td>{{ p.booking_date?.slice(0,10) }}</td>
                  <td>
                    <span class="badge" :style="statusBadge(p.status)">{{ p.status }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <p v-else-if="selectedTrekId" class="text-muted">No participants yet.</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router        = useRouter()
const auth          = useAuthStore()
const activeTab     = ref('Dashboard')
const tabs          = ['Dashboard', 'Manage Treks', 'Participants']
const staffName     = ref('')
const assignedTreks = ref([])
const participants  = ref([])
const selectedTrekId = ref('')
const updateMsg     = ref({})
const slotInputs    = ref({})
const statusSelects = ref({})

function statusBadge(status) {
  const colors = {
    Open:      'background:#4a6741',
    Closed:    'background:#a05c3a',
    Pending:   'background:#8a7a5a',
    Completed: 'background:#3a5a7a',
    Ongoing:   'background:#5a7a3a',
    Booked:    'background:#4a6741',
    Cancelled: 'background:#a05c3a',
  }
  return (colors[status] || 'background:#888') + '; color:white'
}

async function loadDashboard() {
  const res       = await api.get('/staff/dashboard')
  staffName.value = res.data.staff_name
  assignedTreks.value = res.data.assigned_treks
}

async function updateTrek(trekId) {
  const slots  = slotInputs.value[trekId]?.value
  const status = statusSelects.value[trekId]?.value
  const payload = {}
  if (slots)  payload.available_slots = parseInt(slots)
  if (status) payload.status = status

  try {
    await api.put(`/staff/treks/${trekId}`, payload)
    updateMsg.value[trekId] = '✓ Updated successfully'
    await loadDashboard()
    setTimeout(() => updateMsg.value[trekId] = '', 3000)
  } catch (e) {
    updateMsg.value[trekId] = e.response?.data?.message || 'Error'
  }
}

async function markStarted(trekId) {
  await api.post(`/staff/treks/${trekId}/mark-started`)
  await loadDashboard()
}

async function markCompleted(trekId) {
  await api.post(`/staff/treks/${trekId}/mark-completed`)
  await loadDashboard()
}

async function loadParticipants() {
  if (!selectedTrekId.value) return
  const res = await api.get(`/staff/treks/${selectedTrekId.value}/participants`)
  participants.value = res.data.participants
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(loadDashboard)
</script>