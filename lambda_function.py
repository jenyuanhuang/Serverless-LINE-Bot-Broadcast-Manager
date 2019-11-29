from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage
)
import datetime
from argparse import ArgumentParser
import errno
import json
import logging
import os
import requests
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
admin_user_id = os.getenv('LINE_ADMIN_USER_ID')
                               
def lambda_handler(event, context):

    try:
        # get X-Line-Signature header value
        signature = event['headers']['X-Line-Signature']
        # get event body
        body = event['body']
        # handle webhook body
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {'statusCode': 400, 'body': 'InvalidSignature'}
    except Exception as e:
        return {'statusCode': 400, 'body': json.dump(e)}
    return {'statusCode': 200, 'body': 'OK'}
    

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    current_user_id = event.source.user_id

    if current_user_id == admin_user_id:
        if text == 'profile':
            if isinstance(event.source, SourceUser):
                profile = line_bot_api.get_profile(event.source.user_id)
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='Display name: ' + profile.display_name),
                        TextSendMessage(text='Status message: ' + str(profile.status_message))
                    ]
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Bot can't use profile API without user ID"))
        elif text == 'quota':
            quota = line_bot_api.get_message_quota()
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='type: ' + quota.type),
                    TextSendMessage(text='value: ' + str(quota.value))
                ]
            )
        elif text == 'quota_consumption':
            quota_consumption = line_bot_api.get_message_quota_consumption()
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='total usage: ' + str(quota_consumption.total_usage)),
                ]
            )
        elif text == 'push':
            line_bot_api.push_message(
                event.source.user_id, [
                    TextSendMessage(text='PUSH!'),
                ]
            )
        elif text == 'multicast':
            line_bot_api.multicast(
                [event.source.user_id], [
                    TextSendMessage(text='THIS IS A MULTICAST MESSAGE'),
                ]
            )
        elif text == 'broadcast':
            line_bot_api.broadcast(
                [
                    TextSendMessage(text='THIS IS A BROADCAST MESSAGE'),
                ]
            )
        elif text.startswith('broadcast '):  # broadcast 20190505
            date = text.split(' ')[1]
            print("Getting broadcast result: " + date)
            result = line_bot_api.get_message_delivery_broadcast(date)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Number of sent broadcast messages: ' + date),
                    TextSendMessage(text='status: ' + str(result.status)),
                    TextSendMessage(text='success: ' + str(result.success)),
                ]
            )
        elif text == 'bye':
            if isinstance(event.source, SourceGroup):
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Leaving group'))
                line_bot_api.leave_group(event.source.group_id)
            elif isinstance(event.source, SourceRoom):
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Leaving group'))
                line_bot_api.leave_room(event.source.room_id)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Bot can't leave from 1:1 chat"))
        elif text == 'image':
            url = 'https://www.wired.com/wp-content/uploads/2016/07/PikachuTA-EWEATA-1024x768.jpg'
            line_bot_api.broadcast(
                ImageSendMessage(url, url)
            )
        elif text == 'confirm':
            confirm_template = ConfirmTemplate(text='Do it?', actions=[
                MessageAction(label='Yes', text='Yes!'),
                MessageAction(label='No', text='No!'),
            ])
            template_message = TemplateSendMessage(
                alt_text='Confirm alt text', template=confirm_template)
            line_bot_api.broadcast(template_message)
        elif text == 'buttons':
            buttons_template = ButtonsTemplate(
                title='My buttons sample', text='Hello, my buttons', actions=[
                    URIAction(label='Go to line.me', uri='https://line.me'),
                    PostbackAction(label='ping', data='ping'),
                    PostbackAction(label='ping with text', data='ping', text='ping'),
                    MessageAction(label='Translate Rice', text='米')
                ])
            template_message = TemplateSendMessage(
                alt_text='Buttons alt text', template=buttons_template)
            line_bot_api.broadcast(template_message)
        elif text == 'carousel':
            carousel_template = CarouselTemplate(columns=[
                CarouselColumn(text='hoge1', title='fuga1', actions=[
                    URIAction(label='Go to line.me', uri='https://line.me'),
                    PostbackAction(label='ping', data='ping')
                ]),
                CarouselColumn(text='hoge2', title='fuga2', actions=[
                    PostbackAction(label='ping with text', data='ping', text='ping'),
                    MessageAction(label='Translate Rice', text='米')
                ]),
            ])
            template_message = TemplateSendMessage(
                alt_text='Carousel alt text', template=carousel_template)
            line_bot_api.broadcast(template_message)
        elif text == 'image_carousel':
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                    action=DatetimePickerAction(label='datetime',
                                                                data='datetime_postback',
                                                                mode='datetime')),
                ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                    action=DatetimePickerAction(label='date',
                                                                data='date_postback',
                                                                mode='date'))
            ])
            template_message = TemplateSendMessage(
                alt_text='ImageCarousel alt text', template=image_carousel_template)
            line_bot_api.broadcast(template_message)
        elif text == 'imagemap':
            pass
        elif text == 'flex':
            bubble = BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    url='https://example.com/cafe.jpg',
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
                    action=URIAction(uri='http://example.com', label='label')
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        # title
                        TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                        # review
                        BoxComponent(
                            layout='baseline',
                            margin='md',
                            contents=[
                                IconComponent(size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(size='sm', url='https://example.com/grey_star.png'),
                                IconComponent(size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(size='sm', url='https://example.com/grey_star.png'),
                                TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                              flex=0)
                            ]
                        ),
                        # info
                        BoxComponent(
                            layout='vertical',
                            margin='lg',
                            spacing='sm',
                            contents=[
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Place',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text='Shinjuku, Tokyo',
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
                                    ],
                                ),
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Time',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text="10:00 - 23:00",
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5,
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        # callAction, separator, websiteAction
                        SpacerComponent(size='sm'),
                        # callAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(label='CALL', uri='tel:000000'),
                        ),
                        # separator
                        SeparatorComponent(),
                        # websiteAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(label='WEBSITE', uri="https://example.com")
                        )
                    ]
                ),
            )
            message = FlexSendMessage(alt_text="hello", contents=bubble)
            line_bot_api.broadcast(
                message
            )
        elif text == 'flex_update_1':
            bubble_string = """
            {
              "type": "bubble",
              "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "image",
                    "url": "https://line-objects-dev.com/flex/bg/eiji-k-1360395-unsplash.jpg",
                    "position": "relative",
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "1:1",
                    "gravity": "center"
                  },
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "text": "Brown Hotel",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#ffffff"
                          },
                          {
                            "type": "box",
                            "layout": "baseline",
                            "margin": "md",
                            "contents": [
                              {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                              },
                              {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                              },
                              {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                              },
                              {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                              },
                              {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
                              },
                              {
                                "type": "text",
                                "text": "4.0",
                                "size": "sm",
                                "color": "#d6d6d6",
                                "margin": "md",
                                "flex": 0
                              }
                            ]
                          }
                        ]
                      },
                      {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "text": "¥62,000",
                            "color": "#a9a9a9",
                            "decoration": "line-through",
                            "align": "end"
                          },
                          {
                            "type": "text",
                            "text": "¥42,000",
                            "color": "#ebebeb",
                            "size": "xl",
                            "align": "end"
                          }
                        ]
                      }
                    ],
                    "position": "absolute",
                    "offsetBottom": "0px",
                    "offsetStart": "0px",
                    "offsetEnd": "0px",
                    "backgroundColor": "#00000099",
                    "paddingAll": "20px"
                  },
                  {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {
                        "type": "text",
                        "text": "SALE",
                        "color": "#ffffff"
                      }
                    ],
                    "position": "absolute",
                    "backgroundColor": "#ff2600",
                    "cornerRadius": "20px",
                    "paddingAll": "5px",
                    "offsetTop": "10px",
                    "offsetEnd": "10px",
                    "paddingStart": "10px",
                    "paddingEnd": "10px"
                  }
                ],
                "paddingAll": "0px"
              }
            }
            """
            message = FlexSendMessage(alt_text="hello", contents=json.loads(bubble_string))
            line_bot_api.broadcast(
                message
            )
        elif text == 'quick_reply':
            line_bot_api.broadcast(
                TextSendMessage(
                    text='Quick reply',
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(label="label1", data="data1")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="label2", text="text2")
                            ),
                            QuickReplyButton(
                                action=DatetimePickerAction(label="label3",
                                                            data="data3",
                                                            mode="date")
                            ),
                            QuickReplyButton(
                                action=CameraAction(label="label4")
                            ),
                            QuickReplyButton(
                                action=CameraRollAction(label="label5")
                            ),
                            QuickReplyButton(
                                action=LocationAction(label="label6")
                            ),
                        ])))
        elif text == 'link_token' and isinstance(event.source, SourceUser):
            link_token_response = line_bot_api.issue_link_token(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='link_token: ' + link_token_response.link_token)
                ]
            )
        elif text == 'insight_message_delivery':
            today = datetime.date.today().strftime("%Y%m%d")
            response = line_bot_api.get_insight_message_delivery(today)
            if response.status == 'ready':
                messages = [
                    TextSendMessage(text='broadcast: ' + str(response.broadcast)),
                    TextSendMessage(text='targeting: ' + str(response.targeting)),
                ]
            else:
                messages = [TextSendMessage(text='status: ' + response.status)]
            line_bot_api.reply_message(event.reply_token, messages)
        elif text == 'insight_followers':
            today = datetime.date.today().strftime("%Y%m%d")
            response = line_bot_api.get_insight_followers(today)
            if response.status == 'ready':
                messages = [
                    TextSendMessage(text='followers: ' + str(response.followers)),
                    TextSendMessage(text='targetedReaches: ' + str(response.targeted_reaches)),
                    TextSendMessage(text='blocks: ' + str(response.blocks)),
                ]
            else:
                messages = [TextSendMessage(text='status: ' + response.status)]
            line_bot_api.reply_message(event.reply_token, messages)
        elif text == 'insight_demographic':
            response = line_bot_api.get_insight_demographic()
            if response.available:
                messages = ["{gender}: {percentage}".format(gender=it.gender, percentage=it.percentage)
                            for it in response.genders]
            else:
                messages = [TextSendMessage(text='available: false')]
            line_bot_api.reply_message(event.reply_token, messages)
        else:
            line_bot_api.broadcast(TextSendMessage(text=event.message.text))
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text))

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    
    current_user_id = event.source.user_id

    if current_user_id == admin_user_id:
        line_bot_api.broadcast(
            StickerSendMessage(
                package_id=event.message.package_id,
                sticker_id=event.message.sticker_id)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            StickerSendMessage(
                package_id=event.message.package_id,
                sticker_id=event.message.sticker_id)
        )
    
@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.data))