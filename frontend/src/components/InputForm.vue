<template>
  <v-container>
    <h1 class="text-center move text-h2 font-weight-bold mt-10 text-blue-grey-darken-3">SPOTI-TUBE</h1>
    <h1 class="text-center text-h4 mb-10">Convert Your Spotify Playlist to Your Device</h1>

    <v-sheet class="d-flex flex-wrap">
      <v-text-field
        v-model="url"
        label="Enter the Spotify Playlist Link"
        class="mr-4"
      ></v-text-field>
      <v-btn
        class="text-white"
        color="blue-grey darken-1"
        size="x-large"
        prepend-icon="mdi-download"
        @click.prevent="performSearch"
      >
        Download
      </v-btn>
    </v-sheet>
    <h1 class="text-center text-h6 text-red" v-if="correct">INVALID URL</h1>
    <br>
    <h1 class="text-center text-h4 font-weight-bold text-blue-grey-darken-3 mt-5" v-if="showDetails">Playlist Details</h1>
    <hr v-if="showDetails" class="mt-5">

    <div class="text-center">
      <p class="text-center font-weight-bold text-blue-grey-darken-3 mt-1" v-if="loader">Loading Details....</p>
      <p class="text-center font-weight-bold text-blue-grey-darken-3 mt-1" v-if="statusMessage">{{ statusMessage }}</p>
    </div>

    <v-row v-if="showDetails" class="mt-5">
      <v-col v-for="track in playlistDetails" :key="track.uri" cols="12" md="6" lg="4">
        <v-card @click="showSongDetails(track)">
          <v-img :src="track.image_url" height="200px"></v-img>
          <v-card-title>{{ track.name }}</v-card-title>
          <v-card-subtitle>{{ track.artists }}</v-card-subtitle>
          <v-card-text>
            <div><strong>Album:</strong> {{ track.album_name }}</div>
            <div><strong>Release Date:</strong> {{ track.album_release_date }}</div>
          </v-card-text>
          <v-card-actions>
            <div class="text-center">
              <v-btn :href="track.preview_url" target="_blank">Preview</v-btn>
              <v-btn class="bg-blue-grey-darken-3" @click.prevent="downloadSong(track.uri)">Download</v-btn>
            </div>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Song details dialog -->
    <v-dialog v-model="dialogVisible" max-width="600">
      <v-card>
        <v-img :src="selectedTrack.image_url" class="mt-2" height="200px"></v-img>
        <v-card-title class="mt-3 ms-3 text-center"><strong>Song Name  : </strong>{{ selectedTrack.name }}</v-card-title>
        <v-card-text>
          <div><strong>Artists :</strong> {{ selectedTrack.artists }}</div>
          <div><strong>Album :</strong> {{ selectedTrack.album_name }}</div>
          <div><strong>Release Date :</strong> {{ selectedTrack.album_release_date }}</div>
          <div><strong>Album Type  :</strong> {{ selectedTrack.album_type }}</div>
          <div><strong>Popularity  :</strong> {{ selectedTrack.popularity }}</div>
          <div><strong>Duration  :</strong> {{ millisecondsToMinutesSeconds(selectedTrack.duration_ms) }} Minutes</div>
          <v-card-actions>
            <div class="move-left">
              <v-btn :href="selectedTrack.preview_url" target="_blank">Preview</v-btn>
              <v-btn class="bg-blue-grey-darken-3" @click.prevent="downloadSong(selectedTrack.uri)">Download</v-btn>
            </div>
          </v-card-actions>

        </v-card-text>
        <v-card-actions>
          <v-btn @click="dialogVisible = false" class="bg-blue-grey-darken-3">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <div class="text-center mt-5" v-if="showDetails">
      <v-btn class="bg-blue-grey-darken-3" prepend-icon="mdi-download" @click.prevent="downloadAllSongs">Download Playlist</v-btn>
    </div>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      url: '',
      correct: false,
      showDetails: false,
      loader: false,
      safeUrl: '',
      playlistDetails: [],
      statusMessage: '',
      dialogVisible: false,
      selectedTrack: {},
      socket: null
    };
  },
  methods: {
    async performSearch() {
      const regex = /playlist\/([a-zA-Z0-9]+)\?/;
      const match = this.url.match(regex);
      if (match && match[1]) {
        this.safeUrl = match[1];
        this.url = '';
        this.correct = false;
        this.showDetails = true;
        this.loader = true;

        try {
          const response = await axios.post('http://localhost:8000/getDetails', {
            id: match[1]
          });

          this.playlistDetails = response.data;
          this.loader = false;
        } catch (error) {
          console.log(error);
        }
      } else {
        this.url = '';
        this.correct = true;
        this.showDetails = false;
      }
    },
      millisecondsToMinutesSeconds(milliseconds) {
            let totalSeconds = milliseconds / 1000;
            let minutes = Math.floor(totalSeconds / 60);
            let seconds = Math.floor(totalSeconds % 60);
            return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
      },
    showSongDetails(track) {
      this.selectedTrack = track;
      this.dialogVisible = true;
    },
    async downloadSong(uri) {
      try {
        const response = await fetch('http://localhost:8000/downloadSong', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ id: uri })
        });
        console.log("GGGGGGGG")

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        console.log(a.href)
        a.download = 'song.mp3';
        document.body.appendChild(a);
        a.click();
        console.log("Downloaded")
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error downloading song:', error);
      }
    },
    async downloadAllSongs() {
      this.socket = new WebSocket('ws://localhost:8000/ws');

      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.socket.send(`download:${this.safeUrl}`);
      };

      this.socket.onmessage = async (event) => {
        if (event.data instanceof Blob) {
          try {
            const blob = event.data;
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = 'song.mp3';
            document.body.appendChild(a);

            a.click();

            window.URL.revokeObjectURL(url);
          } catch (error) {
            console.error('Error downloading song:', error);
          }
        } else {
          console.log('WebSocket message received:', event.data);
          this.statusMessage = event.data;
        }
      };

      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
      };

      try {
        const response = await axios.post('http://localhost:8000/downloadAllSongs', {
          id: this.safeUrl
        });
        console.log(response.data);
      } catch (error) {
        console.log(error);
      }
    }
    }
};
</script>

<style scoped>
.move {
  margin-top: 100px !important;
}
.move-left {
  margin-left: -16px;
}
</style>
