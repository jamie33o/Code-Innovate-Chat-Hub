import bleach
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from group_chat.models import PostsModel, CommentsModel
from group_chat.forms import CommentsForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(login_required, name='dispatch')
class CommentsView(View):
    template_name = 'group_chat/comments.html'

    def get(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(PostsModel, id=post_id)
        comments = CommentsModel.objects.filter(comment_post=post)

        form = CommentsForm()

        context = {
            'post': post,
            'comments': comments,
            'form': form,
        }

        return render(request, self.template_name, context)

    def post(self, request, post_id, *args, **kwargs):
        form = CommentsForm(request.POST)
        if form.is_valid():
            form.instance.comment_post = get_object_or_404(PostsModel, id=post_id)

            comment = self.process_and_save(request, form)
            #self.broadcast_comment(request, comment, post_id)

            redirect_url = reverse('post_comments', args=[post_id])
            return redirect(redirect_url)
        else:
            print(form.errors)
            # return response with error message

    def process_and_save(self, request, form):
        comment = form.save(commit=False)
        # allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img', 'ol', 'li', 'div', 'span', 'a']
        # allowed_attributes = {'*': ['style', 'src', 'href','class']}
        # allowed_styles = ['display', 'width', 'height', 'background', 'background-size']

        # comment.post = bleach.clean(comment.post, tags=allowed_tags, attributes=allowed_attributes, styles=allowed_styles)
        comment.created_by = request.user
        comment.save()

        return comment
    def broadcast_comment(self, request, comment, post_id):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"comment_post{post_id}",
            {
                'type': 'comment_notification',
                'message': 'New post added!',
                'comment_content': comment.post,
                'comment_creator': request.user.username,
            }
        )
