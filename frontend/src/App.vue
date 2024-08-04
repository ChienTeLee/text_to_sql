<template>
  <div id="app">
    <h1>Text to SQL</h1>
    <form @submit.prevent="textToSQL">
      <div>
        <label for="user">User Name:</label>
        <input type="text" id="user" v-model="user" required>
      </div>
      <div>
        <label for="query">Text Input:</label>
        <textarea id="query" v-model="query" required></textarea>
      </div>
      <button type="submit">Text to SQL</button>
    </form>
    <div v-if="responseData" class="response-container">
      <h2>Response:</h2>
      <p><strong>User Name:</strong> {{ responseData.user }}</p>
      <p><strong>Timestamp:</strong> {{ responseData.timestamp }}</p>
      <div class="response-block">
        <strong>Content:</strong>
        <pre><code>{{ responseData.response }}</code></pre>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      user: '',
      query: '',
      responseData: null
    }
  },
  methods: {
    async textToSQL() {
      console.log('textToSQL method called'); // Debug log
      try {
        const timestamp = new Date().toISOString()
        const requestData = {
          user: this.user,
          timestamp: timestamp,
          query: this.query
        }
        
        console.log('Sending request with data:', requestData); // Debug log

        const response = await axios.post('/ask/', requestData, {
          headers: {
            'Content-Type': 'application/json'
          }
        })

        console.log('Received response:', response.data); // Debug log

        this.responseData = response.data
      } catch (error) {
        console.error('Error converting text to SQL:', error)
        if (error.response) {
          console.error('Response status:', error.response.status)
          console.error('Response data:', JSON.stringify(error.response.data, null, 2))
        } else if (error.request) {
          console.error('No response received:', error.request)
        } else {
          console.error('Error setting up request:', error.message)
        }
        this.responseData = {
          user: this.user,
          timestamp: new Date().toISOString(),
          response: 'An error occurred while converting text to SQL.'
        }
      }
    }
  }
}
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

label {
  font-weight: bold;
}

input, textarea {
  width: 100%;
  padding: 5px;
}

button {
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.response-container {
  margin-top: 20px;
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 5px;
}

.response-block {
  margin-top: 10px;
}

.response-block pre {
  background-color: #f4f4f4;
  border: 1px solid #ddd;
  border-left: 3px solid #4CAF50;
  color: #666;
  page-break-inside: avoid;
  font-family: monospace;
  font-size: 15px;
  line-height: 1.6;
  margin-top: 10px;
  max-width: 100%;
  overflow: auto;
  padding: 1em 1.5em;
  display: block;
  word-wrap: break-word;
}
</style>