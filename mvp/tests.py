from django.test import (
    TestCase,
    Client,
)
from django.contrib.auth import get_user_model
from django.conf import settings

from . import views, models, forms


User = get_user_model()


class PhotoTest(TestCase):
    def setUp(self):
        """본 테스트에 공통으로 사용하는 데이터들.
        test users를 만들고 이 이용자가 접근한다는 전제로 사용함.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='test1', password='1')
        self.user2 = User.objects.create_user(username='test2', password='2')

    def _login(self, user_number):
        num = str(user_number)
        # 로그인 시도.
        return self.client.post(
            settings.LOGIN_URL, {'username': 'test' + num, 'password': num}
        )

    def _add_photo(self):
        # 사진 게시 시도.
        return self.client.post('/mvp/photos/create/', {
            'image_url': 'http://blog.hannal.net',
            'description': 'hi world',
        }, follow=True)

    def test_create_photo_by_model(self):
        """모델을 이용해 사진 데이터를 추가하는 테스트
        """
        photo = models.Photo(
            user=self.user,
            image_url='http://blog.hannal.com',
            description='hello world'
        )
        photo.save()
        self.assertIsNotNone(photo.pk)

        expected_photo = models.Photo.objects.latest('pk')
        self.assertEqual(photo.pk, expected_photo.pk)

    def test_create_many_photos__by_model(self):
        """모델을 이용해 사진 데이터를 여러 번 추가하는 테스트
        """
        for i in range(30):
            photo = models.Photo(
                user=self.user,
                image_url='http://blog.hannal.com',
                description='hello world'
            )
            photo.save()
            self.assertIsNotNone(photo.pk)

            expected_photo = models.Photo.objects.latest('pk')
            self.assertEqual(photo.pk, expected_photo.pk)

    def test_404(self):
        """없는 페이지에 접근하는 테스트.
        """
        response = self.client.get('/page_not_found/')
        self.assertEqual(response.status_code, 404)

    def test_create_photo_by_view_on_logout(self):
        """로그아웃 상태에서 뷰 함수를 이용해 사진을 게시하는 테스트.
        """
        # 로그인하지 않은 상태에서 사진 게시 시도.
        response = self._add_photo()

        # 로그인 하지 않았으므로 로그인 URL로 redirect 됐는지 확인.
        self.assertEqual(response.resolver_match.func.__name__, 'login')
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_create_photo_by_view_on_login(self):
        """로그인 상태에서 뷰 함수를 이용해 사진을 게시하는 테스트.
        """
        self._login(1)
        # 사진 게시 시도.
        response = self._add_photo()
        # 가장 마지막에 등록된 사진 데이터를 가져온다.
        latest_photo = models.Photo.objects.latest('pk')
        # 사진 게시 후 해당 개별 사진을 보는 URL로 redirect 했는지 확인.
        self.assertTrue(
            response.redirect_chain[0][0].endswith(
                '/mvp/photos/{}/'.format(latest_photo.pk)
            )
        )
        self.assertEqual(response.redirect_chain[0][1], 302)
        # 이동한 URL의 뷰 함수가 detail_photo 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.detail_photo)

    def test_create_photo_by_view_with_required_form(self):
        """뷰 함수를 이용해 사진을 게시하는 테스트 중 필수 입력 폼 테스트.
        """
        self._login(1)

        # 필수 입력 항목인 image_url 을 빠뜨리고 사진 게시 시도.
        response = self.client.post('/mvp/photos/create/', {
            'description': 'hi world',
        }, follow=True)
        # http status가 400 인지 테스트. http response에 `status` 인자를 직접 지정해야 함.
        self.assertEqual(response.status_code, 400)
        # 게시에 사용한 폼 인스턴스 객체가 템플릿 컨텍스트에 있는지 테스트.
        self.assertIn('form', response.context)
        # 템플릿 변수인 form에 image_url 폼 필드에 대해 오류가 있는지 테스트.
        self.assertTrue(response.context['form'].has_error('image_url'))

    def test_create_photo_by_view_with_invalid_form(self):
        """뷰 함수를 이용해 사진을 게시하는 테스트 중 잘못된 폼값 테스트.
        """
        self._login(1)

        # image_url을 URL 형식이 아닌 문자열로 게시 시도
        response = self.client.post('/mvp/photos/create/', {
            'image_url': 'not url data',
            'description': 'hi world',
        }, follow=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].has_error('image_url'))

    def test_list_photo(self):
        """사진 목록이 의도대로 동작하는지 테스트.
        """
        self._login(1)
        self._add_photo()

        photos = models.Photo.objects.all()
        # 사진 목록 페이지 접근.
        response = self.client.get('/mvp/photos/', follow=True)
        # http status code가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 이동한 URL의 뷰 함수가 list_photo 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.list_photo)
        # 템플릿 컨텍스트에 photos가 있는지 확인.
        self.assertIn('photos', response.context)
        # 템플릿 변수 photos의 데이터 개수 가져오기.
        res_count = response.context['photos'].count()
        # 그 개수가 한 개인지 확인. (한 번만 넣었으므로)
        self.assertEqual(res_count, 1)
        # 모델로 가져온 데이터 개수와 같은지 비교.
        self.assertEqual(photos.count(), res_count)

    def test_detail_photo(self):
        """개별 사진 페이지가 의도대로 동작하는지 테스트.
        """
        self._login(1)
        self._add_photo()

        # 게시한 사진의 개별 사진 보기 URL 접근.
        response = self.client.get('/mvp/photos/1/', follow=True)
        # http status code가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 이동한 URL의 뷰 함수가 detail_photo 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.detail_photo)
        # 템플릿 컨텍스트에 photo가 있는지 확인.
        self.assertIn('photo', response.context)
        # 그 photo의 pk가 1인지 확인.
        self.assertEqual(response.context['photo'].pk, 1)

    def test_detail_photo_not_exists(self):
        """존재하지 않는 개별 사진 페이지에 접속하여 404가 뜨는지 테스트.
        """
        self._login(1)
        self._add_photo()

        # 존재하지 않는 사진에 접근.
        response = self.client.get('/mvp/photos/133/', follow=True)
        # http status가 404인지 확인.
        self.assertEqual(response.status_code, 404)
        # 응답 페이지가 개별 사진 보는 템플릿이 아닌지 확인.
        self.assertNotIn(
            'detail_photo.html', [tpl.name for tpl in response.templates]
        )

        # 존재하지 않는 사진에 접근.
        response = self.client.get('/mvp/photos/aaa/', follow=True)
        # http status가 404인지 확인.
        self.assertEqual(response.status_code, 404)
        # 응답 페이지가 개별 사진 보는 템플릿이 아닌지 확인.
        self.assertNotIn(
            'detail_photo.html', [tpl.name for tpl in response.templates]
        )

    def test_delete_photo_on_logout(self):
        """로그아웃 상태에서 개별 사진을 지우는 테스트.
        """
        self._login(1)
        self._add_photo()

        # test1 로그아웃
        self.client.get('/logout/')

        # 로그인하지 않고 삭제 url 접근
        response = self.client.get('/mvp/photos/1/delete/', follow=True)
        # 로그인 URL로 redirect 됐는지 확인.
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_delete_photo_bad_request_method(self):
        """개별 사진을 지우는 동작을 GET method로 시도하는 테스트.
        """
        self._login(1)
        self._add_photo()

        # http method GET으로 접근.
        response = self.client.get('/mvp/photos/1/delete/', follow=True)
        # 이동한 URL의 뷰 함수가 delete_photo 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.delete_photo)
        # http status가 405인지 확인.
        self.assertEqual(response.status_code, 405)

    def test_delete_photo_on_another_account(self):
        """다른 사용자가 게시한 개별 사진을 지우는 테스트.
        """
        self._login(1)
        self._add_photo()
        # test1 로그아웃
        self.client.get('/logout/')

        # test2로 로그인 시도.
        self._login(2)

        # http method POST으로 접근.
        response = self.client.post('/mvp/photos/1/delete/', follow=True)
        # 남의 사진을 지우려 한 것이므로 http status가 403인지 확인.
        self.assertEqual(response.status_code, 403)

    def test_delete_photo_successfully(self):
        """사진 게시물 삭제가 잘 됐는지 테스트.
        """
        self._login(1)
        self._add_photo()

        # http method POST으로 접근.
        response = self.client.post('/mvp/photos/1/delete/', follow=True)
        # http status가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 이동한 URL의 뷰 함수가 list_photo 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.list_photo)
        # 모델을 이용해 삭제한 사진이 존재하지 않는지 확인.
        self.assertFalse(models.Photo.objects.filter(pk=1).exists())
        # 삭제한 사진의 개별 사진 URL에 접근.
        response = self.client.get('/mvp/photos/1/', follow=True)
        # 삭제한 사진이므로 http status code는 404.
        self.assertEqual(response.status_code, 404)


class CommentTest(TestCase):
    def setUp(self):
        """본 테스트에 공통으로 사용하는 데이터들.
        test users를 만들고 이 이용자가 접근한다는 전제로 사용함.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='test1', password='1')
        self.user2 = User.objects.create_user(username='test2', password='2')
        self.photo = models.Photo(
            user=self.user,
            image_url='http://blog.hannal.com',
            description='hello world'
        )
        self.photo.save()

    def _login(self, user_number):
        num = str(user_number)
        # 로그인 시도.
        return self.client.post(
            settings.LOGIN_URL, {'username': 'test' + num, 'password': num}
        )

    def _add_comment(self):
        # 댓글 추가 시도.
        return self.client.post(
            '/mvp/photos/{}/comment/'.format(self.photo.pk),
            {
                'content': 'hi world',
            }, follow=True
        )

    def test_create_comment_by_model(self):
        """모델을 이용해 댓글 데이터를 추가하는 테스트
        """
        comment = models.Comment(
            user=self.user,
            photo=self.photo,
            content='hello world'
        )
        comment.save()
        self.assertIsNotNone(comment.pk)

        expected_comment = models.Comment.objects.latest('pk')
        self.assertEqual(comment.pk, expected_comment.pk)

    def test_create_many_comments_by_model(self):
        """모델을 이용해 댓글 데이터를 여러 번 추가하는 테스트
        """
        for i in range(30):
            comment = models.Comment(
                user=self.user,
                photo=self.photo,
                content='hello world'
            )
            comment.save()
            self.assertIsNotNone(comment.pk)

            expected_comment = models.Comment.objects.latest('pk')
            self.assertEqual(comment.pk, expected_comment.pk)

    def test_create_comment_by_view_on_logout(self):
        """로그아웃 상태에서 뷰를 이용해 댓글 데이터를 추가하는 테스트
        """
        # 로그인하지 않고 댓글 추가 url 접근
        response = self.client.get('/mvp/photos/1/comment/', follow=True)
        # 로그인 URL로 redirect 됐는지 확인.
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_create_comment_page_by_view_on_login(self):
        """로그아웃 상태에서 댓글 다는 페이지가 나타나는지 테스트.
        """
        # 로그인 시도.
        self._login(1)

        response = self.client.get('/mvp/photos/1/comment/', follow=True)
        # http status가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 이동한 URL의 뷰 함수가 create_comment 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.create_comment)
        # http method GET으로 접근하면 그냥 개별 사진 보는 페이지와 동일한 화면이 나오므로
        # 템플릿 컨텍스트에 photo와 댓글 생성 form이 있는지 확인.
        self.assertIn('photo', response.context)
        self.assertIn('form', response.context)
        # 그 photo의 pk가 1인지 확인.
        self.assertEqual(response.context['photo'].pk, 1)
        # form이 CommentForm의 인스턴스 객체인지 확인
        self.assertIsInstance(response.context['form'], forms.CommentForm)

    def test_post_create_comment_by_view_on_logout(self):
        """로그아웃 상태에서 댓글 추가 시도하는 테스트.
        """
        # 댓글 추가 시도.
        response = self._add_comment()

        # http status가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 로그인 URL로 redirect 됐는지 확인.
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_post_create_comment_by_view_on_login(self):
        """로그인 상태에서 댓글 추가 시도하는 테스트.
        """
        # 로그인 시도.
        self._login(1)
        # 댓글 추가 시도.
        response = self._add_comment()

        # http status가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 이동한 URL의 뷰 함수가 detail_photo 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.detail_photo)
        # 템플릿 컨텍스트에 photo이 있는지 확인.
        self.assertIn('photo', response.context)
        # 그 photo에 댓글 개수가 총 한 개인지 확인.
        _the_photo = response.context['photo']
        self.assertEqual(_the_photo.comment_set.count(), 1)

    def test_post_create_comment_by_view_invalid_form(self):
        """댓글 본문 없이 댓글 추가 시도하는 테스트.
        """
        # 로그인 시도.
        self._login(1)

        # 댓글 본문 없이 댓글 추가 시도.
        response = self.client.post(
            '/mvp/photos/{}/comment/'.format(self.photo.pk), follow=True
        )
        # http status가 400 인지 테스트. http response에 `status` 인자를 직접 지정해야 함.
        self.assertEqual(response.status_code, 400)
        # 게시에 사용한 폼 인스턴스 객체가 템플릿 컨텍스트에 있는지 테스트.
        self.assertIn('form', response.context)
        # 템플릿 변수인 form에 content 폼 필드에 대해 오류가 있는지 테스트.
        self.assertTrue(response.context['form'].has_error('content'))

    def test_post_create_comment_by_view_not_exists_photo(self):
        """댓글 본문 없이 댓글 추가 시도하는 테스트.
        """
        # 로그인 시도.
        self._login(1)

        # 존재하지 않는 사진에 댓글 추가 시도.
        response = self.client.post(
            '/mvp/photos/555/comment/',
            {
                'content': 'hi world',
            }, follow=True
        )
        # http status가 404인지 확인.
        self.assertEqual(response.status_code, 404)

    def test_delete_comment_on_logout(self):
        """로그아웃 상태에서 개별 댓글을 지우는 테스트.
        """
        self._login(1)
        response = self._add_comment()
        # test1 로그아웃
        self.client.get('/logout/')

        # 로그인하지 않고 삭제 url 접근
        response = self.client.get('/mvp/comment/1/delete/', follow=True)
        # 로그인 URL로 redirect 됐는지 확인.
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_delete_comment_bad_request_method(self):
        """GET method로 개별 댓글을 지우는 테스트.
        """
        self._login(1)
        response = self._add_comment()

        # http method GET으로 접근.
        response = self.client.get('/mvp/comment/1/delete/', follow=True)
        # 이동한 URL의 뷰 함수가 delete_comment 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.delete_comment)
        # http status가 405인지 확인.
        self.assertEqual(response.status_code, 405)

    def test_delete_comment_bad_by_another_account(self):
        """다른 사람이 작성한 개별 댓글을 지우는 테스트.
        """
        self._login(1)
        response = self._add_comment()
        # test1 로그아웃
        self.client.get('/logout/')
        self._login(2)

        # http method POST으로 접근.
        response = self.client.post('/mvp/comment/1/delete/', follow=True)
        # 남의 사진을 지우려 한 것이므로 http status가 403인지 확인.
        self.assertEqual(response.status_code, 403)

    def test_delete_comment_successfully(self):
        """자신이 작성한 개별 댓글을 지우는 테스트.
        """
        self._login(1)
        response = self._add_comment()

        # http method POST으로 접근.
        response = self.client.post('/mvp/comment/1/delete/', follow=True)
        # http status가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 이동한 URL의 뷰 함수가 detail_photo 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.detail_photo)
        # 모델을 이용해 삭제한 댓글이 존재하지 않는지 확인.
        self.assertFalse(models.Comment.objects.filter(pk=1).exists())
        # 삭제한 댓글의 개별 사진 URL에 접근.
        response = self.client.get('/mvp/photos/1/', follow=True)
        self.assertEqual(response.status_code, 200)
        # 템플릿 컨텍스트에 photo이 있는지 확인.
        self.assertIn('photo', response.context)
        # 그 photo에 댓글 개수가 총 0개인지 확인.
        _the_photo = response.context['photo']
        self.assertEqual(_the_photo.comment_set.count(), 0)

    def test_delete_comment_not_exists(self):
        """존재하지 않는 개별 댓글을 지우는 테스트.
        """
        self._login(1)

        # 존재하지 않는 댓글 삭제를 시도.
        response = self.client.post('/mvp/comment/555/delete/', follow=True)
        # http status가 404인지 확인.
        self.assertEqual(response.status_code, 404)


class LikeTest(TestCase):
    def setUp(self):
        """본 테스트에 공통으로 사용하는 데이터들.
        test users를 만들고 이 이용자가 접근한다는 전제로 사용함.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='test1', password='1')
        self.user2 = User.objects.create_user(username='test2', password='2')
        self.photo = models.Photo(
            user=self.user,
            image_url='http://blog.hannal.com',
            description='hello world'
        )
        self.photo.save()

    def _login(self, user_number):
        num = str(user_number)
        # 로그인 시도.
        return self.client.post(
            settings.LOGIN_URL, {'username': 'test' + num, 'password': num}
        )

    def test_do_like_by_model(self):
        """모델을 이용해 좋아요 데이터를 추가하는 테스트
        """
        if self.photo.likes.filter(pk=self.user.pk).exists():
            self.photo.likes.remove(self.user)
        else:
            self.photo.likes.add(self.user)
        self.assertTrue(self.photo.likes.filter(pk=self.user.pk).exists())

    def test_do_like_by_view_on_logout(self):
        """로그아웃 상태에서 뷰를 이용해 좋아요 처리하는 테스트
        """
        # 로그인하지 않고 댓글 추가 url 접근
        response = self.client.get('/mvp/photos/1/like/', follow=True)
        # 로그인 URL로 redirect 됐는지 확인.
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_do_like_by_view_not_exists_photo(self):
        """존재하지 않는 사진에 좋아요 처리하는 테스트
        """
        # 로그인 시도.
        self._login(1)

        # 존재하지 않는 사진에 좋아요 시도.
        response = self.client.get('/mvp/photos/555/like/')
        # http status가 404인지 확인.
        self.assertEqual(response.status_code, 404)

    def test_do_like_by_view_own_photo(self):
        """자신의 사진에 좋아요 처리하는 테스트
        """
        # 로그인 시도.
        self._login(1)

        response = self.client.get('/mvp/photos/1/like/', follow=True)
        # 자기 자신에는 좋아요 표시를 남길 수 없으므로 http status가 400인지 확인.
        self.assertEqual(response.status_code, 400)

    def test_do_like_by_view_successfulyy(self):
        """남의 사진에 좋아요 처리하는 테스트
        """
        # 로그인 시도.
        self._login(2)

        # 좋아요 시도.
        response = self.client.get('/mvp/photos/1/like/', follow=True)
        # http status가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 이동한 URL의 뷰 함수가 create_comment 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.detail_photo)
        # 템플릿 컨텍스트에 photo와 댓글 생성 form이 있는지 확인.
        self.assertIn('photo', response.context)
        _the_photo = response.context['photo']
        # 그 photo에 test2 이용자(self.user2)가 like 한 상태인지 확인.
        self.assertTrue(_the_photo.likes.filter(pk=self.user2.pk).exists())

    def test_cancel_like_by_view_successfulyy(self):
        """남의 사진에 남긴 좋아요를 취소하는 테스트.
        """
        # 로그인 시도.
        self._login(2)

        # 좋아요 시도.
        response = self.client.get('/mvp/photos/1/like/', follow=True)
        # http status가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 이동한 URL의 뷰 함수가 create_comment 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.detail_photo)
        # 템플릿 컨텍스트에 photo와 댓글 생성 form이 있는지 확인.
        self.assertIn('photo', response.context)
        _the_photo = response.context['photo']
        # 그 photo에 test2 이용자(self.user2)가 like 한 상태인지 확인.
        self.assertTrue(_the_photo.likes.filter(pk=self.user2.pk).exists())

        # 좋아요 취소 시도.
        response = self.client.get('/mvp/photos/1/like/', follow=True)
        # http status가 200인지 확인.
        self.assertEqual(response.status_code, 200)
        # 이동한 URL의 뷰 함수가 create_comment 인지 테스트.
        self.assertEqual(response.resolver_match.func, views.detail_photo)
        # 템플릿 컨텍스트에 photo와 댓글 생성 form이 있는지 확인.
        self.assertIn('photo', response.context)
        _the_photo = response.context['photo']
        # 그 photo에 like한 이용자에 test2 이용자(self.user2)가 존재하지 않는지 확인.
        self.assertFalse(_the_photo.likes.filter(pk=self.user2.pk).exists())
