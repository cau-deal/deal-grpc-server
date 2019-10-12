from app.services import authService, dealService, missionService

AuthServiceServicer = authService.AuthServiceServicer
dealServiceServicer = dealService.DealServiceServicer
missionServiceServicer = missionService.MissionServiceServicer

# message = messaging.Message(
#     android=messaging.AndroidConfig(
#         ttl=datetime.timedelta(seconds=3600),
#         priority='normal',
#         notification=messaging.AndroidNotification(
#             title='알림인데',
#             body='백그라운드 자비 좀',
#             icon='',
#             color='#f45342',
#             sound='default'
#         ),
#     ),
#     data={
#         'score': '850',
#         'time': '2:45',
#     },
#     topic="all"
#     # token=registration_token
# )

# response = messaging.send(message)
# print(response)