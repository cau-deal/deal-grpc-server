[1mdiff --git a/app/services/missionService.py b/app/services/missionService.py[m
[1mold mode 100644[m
[1mnew mode 100755[m
[1mindex ba2153c..ea574dc[m
[1m--- a/app/services/missionService.py[m
[1m+++ b/app/services/missionService.py[m
[36m@@ -42,19 +42,12 @@[m [mclass MissionServiceServicer(MissionServiceServicer, metaclass=ServicerMeta):[m
         result_message = "Unknown"[m
         register_mission_result = RegisterMissionResult.UNKNOWN_REGISTER_MISSION_RESULT[m
 [m
[31m-        # DB Transaction[m
[31m-        # table : mission[m
[31m-[m
[31m-        # Extract Email[m
[31m-        metadata = dict(context.invocation_metadata())[m
[31m-        _email_addr = (metadata['aud']) if metadata['aud'] else ""[m
[31m-[m
         # JWT.decode()[m
 [m
         with db.atomic() as transaction:[m
             try:[m
                 Mission.create([m
[31m-                    register_email=_email_addr,[m
[32m+[m[32m                    register_email=context.user_email[m[41m[m
                     id=mission_id,[m
                     title=title,[m
                     contents=contents,[m
[36m@@ -130,14 +123,18 @@[m [mclass MissionServiceServicer(MissionServiceServicer, metaclass=ServicerMeta):[m
             try:[m
                 # Keyword NOT Exist[m
                 if(_query_type is NO_KEY_WORD):[m
[32m+[m[32m                    # mission type, _offset, keyword[m[41m[m
                     cursor = db.execute_sql([m
[31m-                        'SELECT mission.id AS id, title, mission_type, price_of_package, deadline, summary, url AS thumbnail_url, mission.created_at AS created_at, mission.state AS state FROM mission, mission_explanation_image WHERE (mission_type = @mission_type AND mission.id > @_offset AND mission.id = mission_explanation_image.mission_id AND mission_explanation_image.image_type = 1 AND (title LIKE @keyword OR contents LIKE @keyword)) ORDER BY id DESC LIMIT 10;'[m
[31m-                        )[m
[32m+[m[32m                        'SELECT mission.id AS id, title, mission_type, price_of_package, deadline, summary, url AS thumbnail_url, mission.created_at AS created_at, mission.state AS state FROM mission, mission_explanation_image WHERE (mission_type = ? AND mission.id > ? AND mission.id = mission_explanation_image.mission_id AND mission_explanation_image.image_type = 1) ORDER BY id DESC LIMIT 10;'[m[41m[m
[32m+[m[32m                        ,(mission_type, _offset),[m[41m[m
[32m+[m[32m                    )[m[41m[m
 [m
                 # Keyword Exist[m
                 else:[m
[32m+[m[32m                    # mission_type, _offset, keyw, keyw[m[41m[m
                     cursor = db.execute_sql([m
[31m-                        'SELECT mission.id AS id, title, mission_type, price_of_package, deadline, summary, url AS thumbnail_url, mission.created_at AS created_at, mission.state AS state FROM mission, mission_explanation_image WHERE (mission_type = @mission_type AND mission.id > @_offset AND mission.id = mission_explanation_image.mission_id AND mission_explanation_image.image_type = 1 AND (title LIKE @keyword OR contents LIKE @keyword)) ORDER BY id DESC LIMIT 10;'[m
[32m+[m[32m                        'SELECT mission.id AS id, title, mission_type, price_of_package, deadline, summary, url AS thumbnail_url, mission.created_at AS created_at, mission.state AS state FROM mission, mission_explanation_image WHERE (mission_type = ? AND mission.id > ? AND mission.id = mission_explanation_image.mission_id AND mission_explanation_image.image_type = 1 AND (title LIKE ? OR contents LIKE ?)) ORDER BY id DESC LIMIT 10;'[m[41m[m
[32m+[m[32m                        ,(mission_type, _offset, keyword, keyword),[m[41m[m
                     )[m
 [m
                 result_code = ResultCode.SUCCESS[m
[36m@@ -150,13 +147,31 @@[m [mclass MissionServiceServicer(MissionServiceServicer, metaclass=ServicerMeta):[m
                 result_message = str(e)[m
                 search_mission_result = SearchMissionResult.FAIL_SEARCH_MISSION_RESULT[m
 [m
[32m+[m[32m            misson_protoes = [][m[41m[m
[32m+[m[41m[m
[32m+[m[32m            # id, title, ms_type, price_of_package, deadline, summary, url, created_at, state,[m[41m[m
[32m+[m[32m            for row in cursor:[m[41m[m
[32m+[m[32m                misson_protoes.append([m[41m[m
[32m+[m[32m                    MissionProto([m[41m[m
[32m+[m[32m                        mission_id = row[0],[m[41m[m
[32m+[m[32m                        title = row[1],[m[41m[m
[32m+[m[32m                        mission_type = row[2],[m[41m[m
[32m+[m[32m                        price_of_package = row[3],[m[41m[m
[32m+[m[32m                        deadline = row[4],[m[41m[m
[32m+[m[32m                        summary = row[5],[m[41m[m
[32m+[m[32m                        mission_state = row[8],[m[41m[m
[32m+[m[32m                        created_at = row[7],[m[41m[m
[32m+[m[32m                        thumbnail_url = row[6],[m[41m                        [m
[32m+[m[32m                    )[m[41m[m
[32m+[m[32m                )[m[41m[m
 [m
         return SearchMissionResponse([m
             result=CommonResult([m
                 result_code=result_code,[m
                 message=result_message[m
             ),[m
[31m-            register_mission_result=search_mission_result[m
[32m+[m[32m            search_mission_result=search_mission_result,[m[41m[m
[32m+[m[32m            mission_protoes = mission_protoes,[m[41m[m
         )[m
 [m
     @verified[m
