트랙이 모두 0개로 표시되는 문제
수정 완료. 변경 내용:           
                                                                                          
  1. _extract_track_count — trackCount / trackcount / track_count 순으로 시도 →                 
  relationships.tracks.meta.total → relationships.tracks.data 길이 순으로 폴백                  
  2. _fetch_track_count — 위 방법 전부 실패하면 트랙 API 직접 호출해서 카운트 (페이지네이션     
  포함)                                                                                         
  3. 동시성 제한 — 동시 요청 3개로 제한 (asyncio.Semaphore)                                   
                                                                                                
  백엔드 재시작하면 반영됩니다. 
  

Graph DB error: Couldn't connect to localhost:7687 (resolved to ('[::1]:7687', '127.0.0.1:7687')): Failed to establish connection to ResolvedIPv6Address(('::1', 7687, 0, 0)) (reason [Errno 111] Connect call failed ('::1', 7687, 0, 0)) Failed to establish connection to ResolvedIPv4Address(('127.0.0.1', 7687)) (reason [Errno 111] Connect call failed ('127.0.0.1', 7687))