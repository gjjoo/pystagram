from django import forms
from blog.models import Post, Comment
from pystagram.widgets import PointWidget


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ('category', 'title', 'content', 'photo', 'lnglat', 'tags', 'origin_url')
        widgets = {
            'lnglat': PointWidget(attrs={'width':'100%', 'height':'250px'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 10:
            raise forms.ValidationError("10자 이상 입력하세요.")
        return title

    def clean(self):
        title = self.cleaned_data.get('title', '')
        content = self.cleaned_data.get('content', '')
        if len(title) < 10 or len(content) < 10:
            raise forms.ValidationError("제목과 내용을 필히 !!! 10자 이상 입력하세요.")
        return self.cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
