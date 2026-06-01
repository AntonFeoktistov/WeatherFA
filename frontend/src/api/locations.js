import apiClient from './client';

export const locationsApi = {
  
  findWeather: (locationName) =>
    apiClient.get('/locations/find', {
      params: { location_name: locationName },
    }),

  getLocations: () => apiClient.get('/locations/'),

  addLocation: (weatherData) => apiClient.post('/locations/add', weatherData),

  updateLocation: (locationName) => apiClient.put(`/locations/${locationName}`),

  deleteLocation: (locationName) => apiClient.delete(`/locations/${locationName}`),
};