from pyfcm import FCMNotification
push_service = FCMNotification(api_key="AAAAisuS5ss:APA91bH5m303tDXY2eQlVAYygRIqH2oRAiiVDxaVnipG-McWJjVX3xWXXIOMauUV0dUhdPnqvrbI5tmZd2zHV9ixULm71m9uWtNNQjnoEIe0bTYgVzYlg32gkds07EJv_6WOC3vnzz-k")

message_title = "Warning"
message_body = "Too hot!"
data_message = {
	"title" : "LoRa System WARNING",
	"body" : "Temparature too high",
	}
# result = push_service.notify_topic_subscribers(topic_name="LORA_SYSTEM", message_body=message_body, message_title=message_title)
result = push_service.notify_topic_subscribers(topic_name="LORA_SYSTEM", data_message=data_message)
print(result)
