import json, requests, random, re
from pprint import pprint

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


#  ------------------------ Fill this with your page access token! -------------------------------
PAGE_ACCESS_TOKEN = "EAAEYZClBnc0YBACZAW0ZAusiH0NEqTDKQ02bcWPPCTRCjxy2KdSEX9Wivo3TKnaQLNYZA9KEDGBm5XBHKcZByGPO0tZAKM5eywTfOZBE2sCCltfvXNaun5FPz204PZAJvpfaLWaoF8WywksuvjWoOFk7xnzGQl2ahjiuMrfGZB3eoISCisFTm4Wek"
VERIFY_TOKEN = "1234567890"


questions = {
        'a': ["""2019.03 - 2020.02\n(1년 활동 후 수료증 발급)"""],
        'b': ["""명지대 인문캠퍼스 재학생/휴학생 중 웹 서비스를 만들고 싶은 사람 누구나!!\n1년 동안 꾸준히, 열심히, 열정적으로 활동 할 수 있는 사람을 모집합니다!!"""],
        'c': ["""2019.02.20 – 2019.03.07\n1차 서류, 2차 면접 평가로 진행됩니다.\n구체적인 모집 일정 및 지원방법은 추후 업로드 될 예정입니다."""],
        'd': ["""교육\nHTML & CSS (Bootstrap)\nPython\nDjango 를 이용한 웹사이트 개발\n주 1회 또는 2회 스터디 진행\n7기 모집 후에 코드카데미 HTML & CSS 부분 과제 진행합니다.\n미리 해 오셔도 괜찮습니다."""],
        'e': ["""일정\n2월 - 20일 7기 모집 시작3월 - 전체 OT 진행\n7월 - 아이디어톤\n8월 - 무박 2일 해커톤\n11월 - 멋쟁이사자처럼 컨퍼런스 (예정)"""],
        'f': ["""자세한 문의는 카카오톡 플러스친구(@likelionmyongji)를 통해 주시면\n감사하겠습니다."""]
         }


# Helper function
def post_facebook_message(fbid, recevied_message):
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    question_text = ''
    for token in tokens:
        if token in questions:
            question_text = random.choice(questions[token])
            break
    if not question_text:
        question_text = "안녕하세요, 명지대학교(서울)\n멋쟁이 사자처럼 챗봇입니다.\na. 활동 기간\nb. 모집 대상\nc. 모집 일정\nd. 1학기 운영 계획\ne. 멋쟁이 사자처럼 일정\nf. 자세한 문의\n중 한 가지 알파벳을 입력해주세요."

    '''
    # 유저 이름 출력(오류 발생, 구현 예정)
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()
    question_text = '질문 주셔서 감사합니다, '+user_details['first_name']+'님!' + question_text
    '''

    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":question_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())

# Create your views here.
class chatbotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()
