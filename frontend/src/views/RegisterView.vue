<template>
  <div class="register-container">
    <div class="card">
      <h1>📝 Регистрация</h1>
      <form @submit.prevent="handleRegister">
        <div class="input-group">
          <label for="name">Имя пользователя</label>
          <input id="name" v-model="name" type="text" placeholder="Ваше имя" />
        </div>

        <div class="input-group">
          <label for="password1">Пароль</label>
          <input id="password1" v-model="password1" type="password" placeholder="••••••" />
        </div>

        <div class="input-group">
          <label for="password2">Подтверждение пароля</label>
          <input id="password2" v-model="password2" type="password" placeholder="••••••" />
        </div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          {{ isLoading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      </form>
      <p class="login-link">
        Уже есть аккаунт? <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const name = ref('');
const password1 = ref('');
const password2 = ref('');
const errorMessage = ref('');
const isLoading = ref(false);
const router = useRouter();
const authStore = useAuthStore();

const handleRegister = async () => {
  if (password1.value !== password2.value) {
    errorMessage.value = 'Пароли не совпадают';
    return;
  }
  
  isLoading.value = true;
  errorMessage.value = '';
  
  try {
    await authStore.register({ 
      name: name.value, 
      password1: password1.value, 
      password2: password2.value 
    });
    router.push('/login');
  } catch (error) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = 'Ошибка регистрации';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>


<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  padding: 16px;
}

.card {
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 35px -10px rgba(0, 0, 0, 0.1);
  padding: 32px 28px;
  width: 100%;
  max-width: 420px;
}

h1 {
  margin: 0 0 28px 0;
  font-size: 1.8rem;
  font-weight: 600;
  text-align: center;
  color: #1e293b;
}

.input-group {
  margin-bottom: 20px;
}

label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 6px;
  color: #334155;
}

input {
  width: 100%;
  padding: 12px 14px;
  font-size: 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  background: #fff;
  transition: 0.2s;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.2);
}

.btn-primary {
  width: 100%;
  background: #42b883;
  color: white;
  font-weight: 600;
  font-size: 1rem;
  padding: 12px;
  border: none;
  border-radius: 40px;
  cursor: pointer;
  transition: background 0.2s ease;
  margin-top: 8px;
}

.btn-primary:hover {
  background: #359f6e;
}

.error {
  color: #e53e3e;
  font-size: 0.85rem;
  margin-top: 12px;
  text-align: center;
}

.login-link {
  text-align: center;
  margin-top: 24px;
  font-size: 0.9rem;
}

a {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

a:hover {
  text-decoration: underline;
}
</style>