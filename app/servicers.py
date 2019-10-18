from app.services import authService, dealService, missionService, phoneService, userService

AuthServiceServicer = authService.AuthServiceServicer
UserServiceServicer = userService.UserServiceServicer
dealServiceServicer = dealService.DealServiceServicer
missionServiceServicer = missionService.MissionServiceServicer
phoneServiceServicer = phoneService.PhoneServiceServicer
userServiceServicer = userService.UserServiceServicer


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