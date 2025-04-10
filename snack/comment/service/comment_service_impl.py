from django.core.exceptions import ObjectDoesNotExist
from comment.repository.comment_repository_impl import CommentRepositoryImpl
from comment.service.comment_service import CommentService
from comment.entity.comment import Comment
from board.entity.board import Board
from account_profile.entity.account_profile import AccountProfile
from utility.auth_utils import is_comment_authorized

class CommentServiceImpl(CommentService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__commentRepository = CommentRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def createComment(self, board: Board, author: AccountProfile, content: str) -> Comment:
        comment = Comment(board=board, author=author, content=content)
        return self.__commentRepository.save(comment)

    def findCommentById(self, comment_id: int) -> Comment:
        return self.__commentRepository.findById(comment_id)

    def findAllCommentsByBoard(self, board: Board) -> list[Comment]:
        return self.__commentRepository.findByBoard(board)

    def findAllCommentsByAuthor(self, author: AccountProfile) -> list[Comment]:
        return self.__commentRepository.findByAuthor(author)

    def deleteComment(self, comment_id: int, userToken: str) -> tuple[bool, int, str]:
        comment = self.__commentRepository.findById(comment_id)
        if not comment:
            return False, 404, "댓글을 찾을 수 없습니다."

        authorized, status_code, message = is_comment_authorized(comment, userToken)
        if not authorized:
            return False, status_code, message

        deleted = self.__commentRepository.delete(comment_id)
        return deleted, 200, "댓글이 삭제되었습니다." if deleted else (False, 500, "삭제 실패")