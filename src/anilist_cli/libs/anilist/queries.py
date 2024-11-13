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
query ({variables}) {{
  Page ({page_query}) {{
    media({media_query}) {{
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
    pageInfo {{
      hasNextPage
      currentPage
      lastPage
      perPage
      total
    }}
  }}
}}
"""

get_expanded_media_info = """
query({variables}) {{
  Media({media_query}) {{
    id
    title {{
      english
      romaji
    }}
    averageScore
    description
    duration
    endDate {{
      day
      month
      year
    }}
    episodes
    chapters
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

update_entry = """
mutation({}) {{
  SaveMediaListEntry({}) {{
    score
    status
    progress
    repeat
    notes
    startedAt {{
      day
      month
      year
    }}
    completedAt {{
      day
      month
      year
    }}
  }}
}}
"""

get_media_list = """
query ({variables}) {{
  MediaListCollection({media_list_query}) {{
    hasNextChunk
    lists {{
      entries {{
        id
        media {{
          title {{
            english
            romaji
          }}
        }}
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
