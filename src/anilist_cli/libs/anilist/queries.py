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
query ({filters}) {{
  Page {{
    media({media_filters}) {{
      id
      title {{
        english
        romaji
      }}
      status
      popularity
      chapters
      episodes
      format
      type
      {list_entry}
    }}
  }}
}}
"""

media_list_entry_query = """
mediaListEntry {
  status
  progress
}
"""
