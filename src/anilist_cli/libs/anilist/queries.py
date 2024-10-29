get_user = """
query {
  Viewer {
    name
    avatar {
      large
    }
    id
    siteUrl
  }
}
"""

get_media = """
query ({filters}) {
  Page {
    media({media_filters}) {
      id
      title {
        english
        romaji
      }
      status
      popularity
      chapters
      episodes
      format
      type
      {list_entry}
    }
  }
}
"""

media_list_entry_query = """
mediaListEntry {
  status
  progress
}
"""

get_sorted_media = """
query ($sort: [MediaSort], $type: MediaType) {
 Page {
   media(sort: $sort, type: $type) {
     id
     title {
       english
       romaji
     }
     status
     popularity
     averageScore
     chapters
     episodes
     format
     type
     mediaListEntry {
       status
       progress
     }
   }
 }
}
"""

get_seasonal_media = """
query($sort: [MediaSort], $status: MediaStatus, $type: MediaType) {
 Page {
   media(sort: $sort, status: $status, type: $type) {
     id
     title {
       english
       romaji
     }
     status
     popularity
     averageScore
     chapters
     episodes
     format
     type
     mediaListEntry {
       status
       progress
     }
   }
 }
}
"""
