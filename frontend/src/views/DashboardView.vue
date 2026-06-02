<template>
  <div class="dashboard">
    <div class="top-bar">
      <h1>🌤 Погода рядом</h1>
      <button @click="logout" class="btn-outline">Выйти</button>
    </div>

    <!-- Поиск погоды -->
    <div class="search-section">
      <div class="search-box">
        <input 
          v-model="searchCity" 
          type="text" 
          placeholder="Введите город (Minsk, Минск)" 
          @keyup.enter="searchWeather"
        />
        <button @click="searchWeather" class="btn-primary" :disabled="isSearching">
          {{ isSearching ? 'Поиск...' : 'Найти' }}
        </button>
      </div>

      <!-- Результат поиска -->
      <div v-if="searchResult" class="weather-result">
        <div class="weather-card found">
          <div class="weather-header">
            <span class="city-name">{{ searchResult.location.name_ru || searchResult.location.name_en }}</span>
            <button @click="addLocation(searchResult)" class="btn-small">➕ Добавить</button>
          </div>
          <div class="weather-details">
            <div class="weather-detail">
              <span class="detail-label">🌡 Температура</span>
              <span class="detail-value">{{ Math.round(searchResult.temperature) }}°C</span>
            </div>
            <div class="weather-detail">
              <span class="detail-label">📝 Состояние</span>
              <span class="detail-value">{{ searchResult.description }}</span>
            </div>
            <div class="weather-detail">
              <span class="detail-label">💨 Ветер</span>
              <span class="detail-value">{{ searchResult.wind_speed }} м/с</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Ошибка поиска -->
      <div v-if="searchError" class="error-message">
        {{ searchError }}
      </div>
    </div>

    <!-- Мои локации -->
    <div class="locations-section">
      <h2>📌 Мои локации</h2>
      
      <div v-if="isLoading" class="loading">
        <div class="spinner"></div>
        <p>Загрузка...</p>
      </div>

      <div v-else-if="locations.length === 0" class="empty-state">
        <p>Пока нет добавленных городов. Найдите и добавьте! 📌</p>
      </div>

      <div class="locations-grid">
        <div v-for="loc in locations" :key="loc.id" class="location-card">
          <div class="card-header">
            <div class="city-info">
              <span class="city-icon">📍</span>
              <strong class="city-title">{{ loc.name_ru || loc.name_en }}</strong>
            </div>
            <div class="actions">
              <button @click="updateLocation(loc.name_en)" class="icon-btn" title="Обновить погоду">🔄</button>
              <button @click="deleteLocation(loc.name_en)" class="icon-btn delete" title="Удалить">🗑️</button>
            </div>
          </div>
          
          <div class="weather-info">
            <div class="weather-item">
              <div class="weather-icon">🌡️</div>
              <div class="weather-data">
                <div class="weather-label">Температура</div>
                <div class="weather-value">{{ Math.round(loc.weather_data.temperature) }}°C</div>
              </div>
            </div>
            <div class="weather-item">
              <div class="weather-icon">📝</div>
              <div class="weather-data">
                <div class="weather-label">Состояние</div>
                <div class="weather-value">{{ loc.weather_data.description }}</div>
              </div>
            </div>
            <div class="weather-item">
              <div class="weather-icon">💨</div>
              <div class="weather-data">
                <div class="weather-label">Ветер</div>
                <div class="weather-value">{{ loc.weather_data.wind_speed }} м/с</div>
              </div>
            </div>
          </div>
          
          <div class="updated-at">
            🕐 {{ formatDate(loc.weather_updated_at) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { locationsApi } from '@/api/locations';

const searchCity = ref('');
const searchResult = ref(null);
const locations = ref([]);
const isLoading = ref(false);
const isSearching = ref(false);
const searchError = ref('');
const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  await fetchLocations();
});

const fetchLocations = async () => {
  isLoading.value = true;
  try {
    const response = await locationsApi.getLocations();
    locations.value = response.data;
  } catch (error) {
    console.error('Ошибка загрузки локаций', error);
  } finally {
    isLoading.value = false;
  }
};

const searchWeather = async () => {
  if (!searchCity.value.trim()) return;
  
  isSearching.value = true;
  searchError.value = '';
  searchResult.value = null;
  
  try {
    const response = await locationsApi.findWeather(searchCity.value);
    searchResult.value = response.data;
  } catch (error) {
    if (error.response?.data?.detail) {
      searchError.value = error.response.data.detail;
    } else {
      searchError.value = 'Не удалось найти погоду. Проверьте название города.';
    }
  } finally {
    isSearching.value = false;
  }
};

const addLocation = async (weatherData) => {
  try {
    await locationsApi.addLocation(weatherData);
    await fetchLocations();
    searchResult.value = null;
    searchCity.value = '';
  } catch (error) {
    if (error.response?.data?.detail) {
      alert(error.response.data.detail);
    } else {
      alert('Ошибка добавления локации');
    }
  }
};

const deleteLocation = async (locationName) => {
  if (confirm(`Удалить город «${locationName}»?`)) {
    try {
      await locationsApi.deleteLocation(locationName);
      await fetchLocations();
    } catch (error) {
      if (error.response?.data?.detail) {
        alert(error.response.data.detail);
      } else {
        alert('Ошибка удаления');
      }
    }
  }
};

const updateLocation = async (locationName) => {
  try {
    await locationsApi.updateLocation(locationName);
    await fetchLocations();
  } catch (error) {
    if (error.response?.data?.detail) {
      alert(error.response.data.detail);
    } else {
      alert('Ошибка обновления погоды');
    }
  }
};

const logout = () => {
  authStore.logout();
  router.push('/login');
};

const formatDate = (dateString) => {
  if (!dateString) return 'ещё не обновлялось';
  const date = new Date(dateString + 'Z');
  return date.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 16px;
  margin-bottom: 28px;
}

h1 {
  margin: 0;
  font-size: 1.8rem;
  background: linear-gradient(135deg, #1e293b, #2d3748);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.btn-outline {
  background: transparent;
  border: 1px solid #cbd5e1;
  padding: 8px 20px;
  border-radius: 40px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: #f1f5f9;
  border-color: #42b883;
}

.search-section {
  background: #f8fafc;
  border-radius: 28px;
  padding: 24px;
  margin-bottom: 40px;
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-box input {
  flex: 1;
  padding: 14px 18px;
  border: 1px solid #cbd5e1;
  border-radius: 60px;
  font-size: 1rem;
  transition: all 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
}

.btn-primary {
  background: #42b883;
  color: white;
  border: none;
  padding: 0 28px;
  border-radius: 60px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #359f6e;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.weather-card {
  background: white;
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.weather-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecef;
}

.city-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
}

.btn-small {
  background: #e9ecef;
  border: none;
  padding: 6px 14px;
  border-radius: 50px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-small:hover {
  background: #42b883;
  color: white;
}

.weather-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.weather-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.detail-label {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 1rem;
  font-weight: 500;
  color: #1e293b;
}

.error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px 20px;
  border-radius: 16px;
  margin-top: 16px;
  font-size: 0.9rem;
}

.locations-section h2 {
  margin-bottom: 20px;
  font-weight: 600;
  color: #1e293b;
}

.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.location-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
  border: 1px solid #edf2f7;
  transition: all 0.25s ease;
}

.location-card:hover {
  box-shadow: 0 16px 28px -12px rgba(0, 0, 0, 0.12);
  transform: translateY(-3px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecef;
}

.city-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.city-icon {
  font-size: 1.2rem;
}

.city-title {
  font-size: 1.1rem;
  color: #1e293b;
}

.actions {
  display: flex;
  gap: 12px;
}

.icon-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #f1f5f9;
  transform: scale(1.05);
}

.icon-btn.delete:hover {
  background: #fee2e2;
}

.weather-info {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 16px;
}

.weather-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.weather-icon {
  font-size: 1.2rem;
  width: 32px;
}

.weather-data {
  flex: 1;
}

.weather-label {
  font-size: 0.7rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.weather-value {
  font-size: 1rem;
  font-weight: 500;
  color: #1e293b;
}

.updated-at {
  font-size: 0.7rem;
  color: #94a3b8;
  text-align: right;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
  margin-top: 8px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #94a3b8;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #42b883;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 32px;
  background: #f8fafc;
  border-radius: 32px;
  color: #475569;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .locations-grid {
    grid-template-columns: 1fr;
  }
  
  .weather-details {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>