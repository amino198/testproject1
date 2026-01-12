from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from .serializers import PostSerializer
from rest_framework import generics
from django.http import JsonResponse
import requests
from django.shortcuts import render

# タイムライン（一覧）表示
def timeline(request):
  posts = Post.objects.select_related('author').order_by('-created_at')
  context = {'posts': posts} # ここで渡しているか
  return render(request, 'timeline.html', context)
    
# 詳細ページ
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'post_detail.html', {'post': post})

# 新規投稿（要ログイン）
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # ログインユーザーを著者に設定
            post.save()
            return redirect('timeline')
    else:
        form = PostForm()
    return render(request, 'post_create.html', {'form': form})

# 編集（要ログイン・本人確認）
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('post_detail', pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'post_edit.html', {'form': form, 'post': post})

# 削除（要ログイン・本人確認）
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('post_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        return redirect('timeline')
    return render(request, 'post_confirm_delete.html', {'post': post})

# ユーザー登録ビュー
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

#検索処理　第８回
# app/views.py

def timeline(request):
    # URLのクエリパラメータから'q'の値を取得する
    query = request.GET.get('q')
    
    if query:
        # クエリがあれば、contentにその文字列を含む投稿をフィルタリング
        # (資料の記述: content_icontains)
        posts = Post.objects.filter(content__icontains=query).order_by('-created_at')
    else:
        # クエリがなければ、全ての投稿を表示
        posts = Post.objects.all().order_by('-created_at')

    context = {
        'posts': posts,
        'query': query, # 検索キーワードをテンプレートに渡す
    }
    return render(request, 'timeline.html', context)

# Postモデルの一覧を返す、API専門のクラスベースビュー
class PostListAPIView(generics.ListAPIView):
    # どのデータの一覧を返すか
    queryset = Post.objects.all()
    
    # どの翻訳者（シリアライザ）を使ってJSONに変換するか
    serializer_class = PostSerializer

@login_required # ログインしていないといいねできないようにする
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    # 既にいいねしている場合は解除、していなければ追加(トグル処理)
    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    # フロントエンドに返すデータを辞書型で作る
    context = {
        'liked': liked, # 今の状態(いいねしたのか、外したのか)
        'count': post.total_likes(), # 最新のいいね数
    }

    # JsonResponseを使ってJSON形式で返却
    return JsonResponse(context)

def weather(request):
    locations = {
        'Kanazawa': {'lat': 36.59, 'lon': 136.60},
        'Tokyo':    {'lat': 35.68, 'lon': 139.76},
        'Osaka':    {'lat': 34.69, 'lon': 135.50},
        'Sapporo':  {'lat': 43.06, 'lon': 141.35},
        'Naha':     {'lat': 26.21, 'lon': 127.68},
    }

    city_name = 'Kanazawa'
    if request.GET.get('city') and request.GET.get('city') in locations:
        city_name = request.GET.get('city')

    lat = locations[city_name]['lat']
    lon = locations[city_name]['lon']

    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true'

    response = requests.get(api_url)
    data = response.json()

    context = {
        'city': city_name,
        'temperature': data['current_weather']['temperature'], 
        'windspeed': data['current_weather']['windspeed'],     
        'weathercode': data['current_weather']['weathercode'], 
    }

    return render(request, 'weather.html', context) 