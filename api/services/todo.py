"""
ToDoアイテムに関するビジネスロジックを実装するサービスモジュール
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from werkzeug.exceptions import BadRequest, Conflict, NotFound

from api.models.todo import Todo, db

# とりあえずメモリ内にデータを保持するようにします
_todos_db = []  # 開発用の一時的なインメモリストレージ
_last_id = 0  # IDを採番するためのカウンター


class TodoService:
    """
    ToDoアイテムのCRUD操作と関連するビジネスロジックを提供するサービスクラス
    """

    @staticmethod
    def get_all_todos(
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_before: Optional[str] = None,
        due_after: Optional[str] = None,
    ) -> list[Todo]:
        """
        全ToDoアイテムを取得し、オプションでフィルタリングする

        Args:
            status: ステータスでフィルタリング (オプション)
            priority: 優先度でフィルタリング (オプション)
            due_before: 指定日より前の期限でフィルタリング (オプション)
            due_after: 指定日より後の期限でフィルタリング (オプション)

        Returns:
            フィルタリングされたToDoアイテムのリスト

        """
        # 実際の実装では、データベースクエリを使用する
        query = Todo.query

        if status:
            query = query.filter(Todo.status == status)
        if priority:
            query = query.filter(Todo.priority == priority)
        if due_before:
            query = query.filter(Todo.due_date <= due_before)
        if due_after:
            query = query.filter(Todo.due_date >= due_after)

        return query.all()

    @staticmethod
    def get_todo_by_id(todo_id: int) -> Dict[str, Any]:
        """
        IDによってToDoアイテムを取得する

        Args:
            todo_id: ToDoアイテムのID

        Returns:
            ToDoアイテム

        Raises:
            NotFound: 指定されたIDのToDoが存在しない場合
        """
        # 実際の実装
        # todo = Todo.query.get(todo_id)
        # if not todo:
        #     raise NotFound(f"ID {todo_id}のToDoは見つかりません")
        # return todo

        # 一時的なインメモリ実装
        for todo in _todos_db:
            if todo["id"] == todo_id:
                return todo

        raise NotFound(f"ID {todo_id}のToDoは見つかりません")

    @staticmethod
    def create_todo(todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        新しいToDoアイテムを作成する

        Args:
            todo_data: 作成するToDoのデータ

        Returns:
            作成されたToDoアイテム

        Raises:
            Conflict: 同じタイトルのToDoが既に存在する場合

        """
        # タイトルの重複チェック
        todos = TodoService.get_all_todos()
        existing_titles = [todo.title for todo in todos]
        if todo_data["title"] in existing_titles:
            msg = "同じタイトルのToDoアイテムが既に存在します"
            raise Conflict(msg)

        new_todo = Todo(
            title=todo_data["title"],
            description=todo_data.get("description"),
            due_date=todo_data.get("due_date"),
            priority=todo_data.get("priority", "medium"),
            status=todo_data.get("status", "not_started"),
        )
        db.session.add(new_todo)
        db.session.commit()
        return new_todo

    @staticmethod
    def update_todo(todo_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        既存のToDoアイテムを更新する

        Args:
            todo_id: 更新するToDoのID
            update_data: 更新データ

        Returns:
            更新されたToDoアイテム

        Raises:
            NotFound: 指定されたIDのToDoが存在しない場合
            Conflict: 更新後のタイトルが他のToDoと重複する場合
        """
        # 実際の実装
        # todo = Todo.query.get(todo_id)
        # if not todo:
        #     raise NotFound(f"ID {todo_id}のToDoは見つかりません")
        #
        # # タイトルが変更され、新しいタイトルが既存のものと重複する場合
        # if 'title' in update_data and update_data['title'] != todo.title:
        #     existing = Todo.query.filter(Todo.title == update_data['title'], Todo.id != todo_id).first()
        #     if existing:
        #         raise Conflict("同じタイトルのToDoアイテムが既に存在します")
        #
        # # 各フィールドを更新
        # for key, value in update_data.items():
        #     if hasattr(todo, key):
        #         setattr(todo, key, value)
        #
        # todo.updated_at = datetime.now()
        # db.session.commit()
        # return todo

        # 一時的なインメモリ実装
        todo = None
        for i, t in enumerate(_todos_db):
            if t["id"] == todo_id:
                todo = t
                todo_index = i
                break

        if todo is None:
            raise NotFound(f"ID {todo_id}のToDoは見つかりません")

        # タイトルが変更され、新しいタイトルが既存のものと重複する場合
        if "title" in update_data and update_data["title"] != todo["title"]:
            for t in _todos_db:
                if t["id"] != todo_id and t["title"] == update_data["title"]:
                    raise Conflict("同じタイトルのToDoアイテムが既に存在します")

        # 各フィールドを更新
        updated_todo = todo.copy()
        for key, value in update_data.items():
            if key in todo:
                updated_todo[key] = value

        updated_todo["updated_at"] = datetime.now().isoformat()
        _todos_db[todo_index] = updated_todo

        return updated_todo

    @staticmethod
    def delete_todo(todo_id: int) -> None:
        """
        ToDoアイテムを削除する

        Args:
            todo_id: 削除するToDoのID

        Raises:
            NotFound: 指定されたIDのToDoが存在しない場合
        """
        # 実際の実装
        # todo = Todo.query.get(todo_id)
        # if not todo:
        #     raise NotFound(f"ID {todo_id}のToDoは見つかりません")
        #
        # db.session.delete(todo)
        # db.session.commit()

        # 一時的なインメモリ実装
        for i, todo in enumerate(_todos_db):
            if todo["id"] == todo_id:
                _todos_db.pop(i)
                return

        raise NotFound(f"ID {todo_id}のToDoは見つかりません")
