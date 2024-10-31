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
query ({}) {{
  Page {{
    media({}) {{
      id
      title {{
        english
        romaji
      }}
      status
      popularity
      averageScore
      chapters
      episodes
      format
      type
      mediaListEntry {{
        progress
        status
        score
      }}
    }}
  }}
}}
"""

get_expanded_media_info = """
query({}) {{
  Media({}) {{
    id
    title {{
      english
      romaji
    }}
    averageScore
    chapters
    description
    duration
    endDate {{
      day
      month
      year
    }}
    episodes
    favourites
    format
    genres
    mediaListEntry {{
      progress
      status
      score
    }}
    popularity
    season
    seasonYear
    source
    startDate {{
      day
      month
      year
    }}
    status
    type
    volumes
  }}
}}
"""

# get_expanded_media_info = """
# query({}) {{
#   Media({}) {{
#     id
#     idMal
#     nextAiringEpisode {{
#       airingAt
#       episode
#       timeUntilAiring
#     }}
#     title {{
#       english
#       romaji
#     }}
#     averageScore
#     chapters
#     countryOfOrigin
#     description
#     duration
#     endDate {{
#       day
#       month
#       year
#     }}
#     episodes
#     favourites
#     format
#     genres
#     meanScore
#     {}
#     popularity
#     rankings {{
#       allTime
#       context
#       format
#       rank
#       season
#       type
#       year
#     }}
#     relations {{
#       nodes {{
#         title {{
#           english
#           romaji
#         }}
#       }}
#     }}
#     recommendations {{
#       nodes {{
#         rating
#         mediaRecommendation {{
#           title {{
#             english
#             romaji
#           }}
#         }}
#       }}
#     }}
#     season
#     seasonYear
#     source
#     startDate {{
#       day
#       month
#       year
#     }}
#     status
#     studios {{
#       nodes {{
#         isAnimationStudio
#         name
#       }}
#     }}
#     synonyms
#     tags {{
#       name
#       isGeneralSpoiler
#       isMediaSpoiler
#     }}
#     type
#     volumes
#   }}
# }}
# """

media_list_entry_preview = """
mediaListEntry {
  progress
  status
  score
}
"""

get_media_list = """
query ({}) {{
  MediaListCollection({}) {{
    hasNextChunk
    lists {{
      entries {{
        id
        media {{
          title {{
            english
            romaji
          }}
          chapters
          episodes
          isFavourite
          status
          type
        }}
        advancedScores
        startedAt {{
          day
          month
          year
        }}
        score
        repeat
        progress
        notes
        completedAt {{
          day
          month
          year
        }}
      }}
      name
      status
    }}
  }}
}}
"""
