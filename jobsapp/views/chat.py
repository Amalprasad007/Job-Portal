from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from django.views import View
from django.views.generic import TemplateView
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
import logging

from jobsapp.models import ChatMessage, User, Job

logger = logging.getLogger(__name__)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ChatView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        if self.request.user.role == 'employee':
            return ['jobs/chat/employee_chat.html']
        return ['jobs/chat/chat.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        other_user_id = self.kwargs.get('user_id')
        job_id = self.kwargs.get('job_id', None)
        
        other_user = get_object_or_404(User, id=other_user_id)
        context['other_user'] = other_user
        
        if job_id:
            context['job'] = get_object_or_404(Job, id=job_id)
        
        messages = ChatMessage.objects.filter(
            (Q(sender=self.request.user, receiver=other_user) |
             Q(sender=other_user, receiver=self.request.user))
        ).order_by('created_at')
        
        context['messages'] = messages
        return context

    def post(self, request, *args, **kwargs):
        try:
            other_user_id = self.kwargs.get('user_id')
            message_text = request.POST.get('message')
            
            if not message_text:
                return JsonResponse({
                    'success': False,
                    'error': 'Message text is required'
                }, status=400)
            
            receiver = get_object_or_404(User, id=other_user_id)
            
            message = ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                content=message_text,
                is_read=False
            )
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'is_sender': True
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                other_user_id = self.kwargs.get('user_id')
                last_message_id = request.GET.get('last_message_id', '0')
                
                other_user = get_object_or_404(User, id=other_user_id)
                
                messages = ChatMessage.objects.filter(
                    (Q(sender=request.user, receiver=other_user) |
                     Q(sender=other_user, receiver=request.user)),
                    id__gt=last_message_id
                ).order_by('created_at')
                
                messages.filter(receiver=request.user).update(is_read=True)
                
                return JsonResponse({
                    'success': True,
                    'messages': [{
                        'id': msg.id,
                        'content': msg.content,
                        'is_sender': msg.sender == request.user
                    } for msg in messages]
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        
        return super().get(request, *args, **kwargs)

class SendMessageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            receiver_id = request.POST.get('receiver_id')
            message_text = request.POST.get('message')
            job_id = request.POST.get('job_id')
            
            print(f"Received message request - receiver: {receiver_id}, message: {message_text}, job: {job_id}")
            
            if not receiver_id or not message_text:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Receiver ID and message text are required'
                    }, status=400)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            
            receiver = get_object_or_404(User, id=receiver_id)
            
            message = ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                content=message_text,
                related_job=Job.objects.get(id=job_id) if job_id else None
            )
            
            print(f"Created message: {message.id}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'is_sender': True
                    }
                })
            
            return HttpResponseRedirect(reverse('jobs:chat', kwargs={'user_id': receiver_id}))
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class GetMessagesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            other_user_id = request.GET.get('user_id')
            last_message_id = request.GET.get('last_id')
            
            if not other_user_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'User ID is required'
                }, status=400)
            
            other_user = get_object_or_404(User, id=other_user_id)
            
            messages_query = ChatMessage.objects.filter(
                (Q(sender=request.user, receiver=other_user) |
                 Q(sender=other_user, receiver=request.user))
            )
            
            if last_message_id:
                messages_query = messages_query.filter(id__gt=last_message_id)
            
            messages = messages_query.order_by('created_at')
            
            return JsonResponse({
                'status': 'success',
                'messages': [{
                    'id': msg.id,
                    'content': msg.content,
                    'is_sender': msg.sender == request.user
                } for msg in messages]
            })
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
