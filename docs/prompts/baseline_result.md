
  VibeGraph 1차 프로토타입 구현 완료                                                                            
                                                                                                              
  생성된 파일 (46개)                                                                                            
                                                                                                              
  VibeGraph/                                                                                                    
  ├── backend/                                                                                                
  │   ├── app/                                                                                                  
  │   │   ├── main.py                          # FastAPI 앱, CORS, 라우터 등록                                
  │   │   ├── core/config.py                   # pydantic-settings 환경변수                                     
  │   │   ├── api/  apple · graph · analysis · recommendations · agent
  │   │   ├── services/                                                                                         
  │   │   │   ├── apple_music_service.py       # Apple Music REST API 호출                                    
  │   │   │   ├── neo4j_service.py             # Cypher 쿼리 (sync · analysis · recommend)                      
  │   │   │   ├── graph_recommendation_service.py                                                               
  │   │   │   ├── agent_service.py             # OpenAI gpt-4o-mini 추천 이유 생성                              
  │   │   │   └── analysis_service.py                                                                           
  │   │   ├── models/schemas.py                # Pydantic 스키마 전체                                           
  │   │   └── utils/errors.py                  # 커스텀 HTTPException                                           
  │   ├── requirements.txt  ·  Dockerfile  ·  .env.example                                                      
  ├── frontend/                                                                                               
  │   ├── src/                                                                                                  
  │   │   ├── App.jsx  ·  main.jsx  ·  index.css (Tailwind)                                                     
  │   │   ├── services/  api.js  ·  musicKit.js
  │   │   ├── components/                                                                                       
  │   │   │   ├── Header · AppleMusicLogin · PlaylistSelector                                                 
  │   │   │   ├── TasteAnalysis · RecommendationList                                                            
  │   │   │   ├── GraphPathView · CreatedPlaylistCard                                                           
  │   │   └── pages/Dashboard.jsx
  │   ├── package.json  ·  vite.config.js  ·  tailwind.config.js                                                
  │   ├── Dockerfile  ·  nginx.conf  ·  .env.example                                                          
  ├── docker-compose.yml                                                                                        
  ├── .gitignore                               # .env, *.p8 포함                                              
  └── README.md                                # 전체 실행 방법 + API 설명                                      
                                                                                                                
  ---                                                                                                           
  실행 방법 요약                                                                                                
                                                                                                              
  Docker Compose (가장 빠름)
  cp backend/.env.example backend/.env                                                                          
  # .env 편집 후                      
  docker-compose up --build                                                                                     
  - 앱: http://localhost                                                                                        
  - API 문서: http://localhost:8000/docs
  - Neo4j Browser: http://localhost:7474                                                                        
                                                                                                                
  ---
  환경변수 필수 설정                                                                                            
                                                                                                                
  ┌─────────────────────┬──────────────────────────────────┬───────────────────────────────────────────┐
  │        위치         │               변수               │                  얻는 곳                  │        
  ├─────────────────────┼──────────────────────────────────┼───────────────────────────────────────────┤      
  │ backend/.env        │ APPLE_MUSIC_DEVELOPER_TOKEN      │ Apple Developer Console → Keys → MusicKit │        
  ├─────────────────────┼──────────────────────────────────┼───────────────────────────────────────────┤      
  │ backend/.env        │ OPENAI_API_KEY                   │ platform.openai.com/api-keys              │        
  ├─────────────────────┼──────────────────────────────────┼───────────────────────────────────────────┤
  │ backend/.env        │ NEO4J_PASSWORD                   │ 직접 설정                                 │        
  ├─────────────────────┼──────────────────────────────────┼───────────────────────────────────────────┤        
  │ frontend/.env.local │ VITE_APPLE_MUSIC_DEVELOPER_TOKEN │ 위와 동일한 JWT                           │
  └─────────────────────┴──────────────────────────────────┴───────────────────────────────────────────┘        
                                                                                                              
  Apple Music Developer Token 생성은 프로젝트 루트의 generate_apple_music_token.py를 사용하세요.                
                                                                                                              
  ---                                                                                                           
  현재 구현의 주요 한계                                                                                       
                                                                                                                
  1. userId 고정 — user_default 하드코딩. 실제 배포 시 다중 사용자 JWT 인증 추가 필요
  2. Artist SIMILAR_TO 미구현 — Last.fm 또는 MusicBrainz API 연동 필요                                          
  3. 추천 알고리즘 단순 — 장르 가중치 기반. PageRank/Node2Vec으로 고도화 가능                                   
  4. MusicKit JS — Safari/Chrome 브라우저 환경 필수 (iOS WebView 별도 처리 필요) 


  