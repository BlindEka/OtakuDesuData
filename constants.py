baseUrl = 'https://otakudesu.cloud/'
ongoingUrl = 'https://otakudesu.cloud/ongoing-anime/'
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
animeSearchPattern = r'\(.+1.+\d{1,3}\)'
episodeSearchPattern = r'(?:episode )(\d{1,3})(?: subtitle indonesia)'

class AnimeDetailsString:
  title = 'judul'
  japanese_title = 'japanese'
  rating = 'skor'
  producer = 'produser'
  type = 'tipe'
  status = 'status'
  episodes = 'total episode'
  duration = 'durasi'
  release_date = 'tanggal rilis'
  studio = 'studio'

class EpisodeDetailsString:
  duration = 'duration'
  type = 'tipe'
  credit = 'credit'
  encoder = 'encoder'
