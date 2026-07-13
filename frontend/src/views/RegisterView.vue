<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center" style="background:#f5f0eb;">
    <div class="card shadow-sm p-4" style="width:420px; border:1px solid #c8b89a;">
      <h4 class="mb-1" style="color:#4a6741;">Trekking Portal</h4>
      <p class="text-muted mb-4" style="font-size:0.9rem;">Create your account</p>

      <div v-if="error" class="alert alert-danger py-2" style="font-size:0.9rem;">{{ error }}</div>
      <div v-if="success" class="alert alert-success py-2" style="font-size:0.9rem;">{{ success }}</div>

      <div class="mb-3">
        <label class="form-label fw-semibold" style="color:#5a4a3a;">Full Name</label>
        <input v-model="form.full_name" type="text" class="form-control" placeholder="Your full name" />
      </div>

      <div class="mb-3">
        <label class="form-label fw-semibold" style="color:#5a4a3a;">Username</label>
        <input v-model="form.username" type="text" class="form-control" placeholder="Choose a username" />
      </div>

      <div class="mb-3">
        <label class="form-label fw-semibold" style="color:#5a4a3a;">Email</label>
        <input v-model="form.email" type="email" class="form-control" placeholder="your@email.com" />
      </div>

      <div class="mb-3">
        <label class="form-label fw-semibold" style="color:#5a4a3a;">Phone (optional)</label>
        <input v-model="form.phone" type="text" class="form-control" placeholder="Your phone number" />
      </div>

      <div class="mb-4">
        <label class="form-label fw-semibold" style="color:#5a4a3a;">Password</label>
        <input v-model="form.password" type="password" class="form-control" placeholder="Choose a password" />
      </div>

      <button @click="handleRegister" class="btn w-100 mb-3" :disabled="loading"
        style="background:#4a6741; color:white;">
        {{ loading ? 'Registering...' : 'Register' }}
      </button>

      <p class="text-center mb-0" style="font-size:0.9rem;">
        Already have an account?
        <router-link to="/login" style="color:#4a6741;">Login here</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router  = useRouter()
const auth    = useAuthStore()
const error   = ref('')
const success = ref('')
const loading = ref(false)

const form = ref({
  full_name: '',
  username:  '',
  email:     '',
  phone:     '',
  password:  '',
})

async function handleRegister() {
  error.value   = ''
  success.value = ''
  loading.value = true
  try {
    await auth.register(form.value)
    success.value = 'Registered successfully! Redirecting to login...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e) {
    error.value = e.response?.data?.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>