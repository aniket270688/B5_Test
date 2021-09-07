from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Create your views here.
from django.http import Http404, HttpResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PostForm
from boards.models import Board, Post, Topic
from django.db.models import Count

from .forms import NewTopicForm

# def home(request):
#     return HttpResponse("Hello world")

def home(request):
    # boards = Board.objects.all()
    # boards_names = []


    # for board in boards:
    #     boards_names.append(board.name)

    # response_html = '<br>'.join(boards_names)
    # print(response_html)

    # return HttpResponse(response_html)

    return render(request, "home.html", context={"all_boards": Board.objects.all()})

@login_required
def board_topics(request, pk):
    # try:
    #     board_obj = Board.objects.get(pk=pk)
    # except Board.DoesNotExist:
    #     raise Http404

    # board_obj = Board.objects.get(pk=pk)
    # print(board_obj)
    board_obj = get_object_or_404(Board, pk=pk)
    return render(request, 'topics.html', {'board': board_obj})

@login_required
def new_topic(request,pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()
    # print(request.user.email)
    # print(request.POST, "In new topic method")
    # return render(request,'new_topic.html',{'board': board})
    user = request.user
    if request.method == 'POST':
        # subject = request.POST['subject']
        # message = request.POST['message']
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()
            post = Post.objects.create(
                message = form.cleaned_data.get('message'),
                topic = topic,
                created_by = user
            )

        # user = User.objects.first()

        # topic = Topic.objects.create(
        #     subject=subject,
        #     board=board,
        #     starter=user
        # )
        
        # post = Post.objects.create(
        #     message=message,
        #     topic=topic,
        #     created_by=user

        # )

            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()    
    return render(request, 'new_topic.html',{'board': board, 'form': form})


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    return render(request, 'topics.html', {'board': board, 'topics': topics})


from django.views.generic import View

class NewPostView(View):
    def render(self, request):
        return render(request, 'new_post.html', {'form': self.form})

    def post(self, request):
        self.form = PostForm(request.POST)
        if self.form.is_valid():
            self.form.save()
            return redirect('post_list')
        return self.render(request)

    def get(self, request):
        self.form = PostForm()
        return self.render(request)