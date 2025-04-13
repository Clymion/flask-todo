"""
ToDoアイテムに関するビジネスロジックを実装するサービスモジュール
"""

from typing import Any, Optional

from werkzeug.exceptions import Conflict, NotFound

from api.models.todo import Todo, db


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
    def get_todo_by_id(todo_id: int) -> dict[str, Any]:
        """
        IDによってToDoアイテムを取得する

        Args:
            todo_id: ToDoアイテムのID

        Returns:
            ToDoアイテム

        Raises:
            NotFound: 指定されたIDのToDoが存在しない場合

        """
        todo = Todo.query.get(todo_id)
        if not todo:
            msg = f"ID {todo_id}のToDoは見つかりません"
            raise NotFound(msg)
        return todo

    @staticmethod
    def create_todo(todo_data: dict[str, Any]) -> dict[str, Any]:
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
    def update_todo(todo_id: int, update_data: dict[str, Any]) -> dict[str, Any]:
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
        todo: Todo | None = Todo.query.get(todo_id)
        if not todo:
            msg = f"ID {todo_id}のToDoは見つかりません"
            raise NotFound(msg)

        # タイトルが変更され、新しいタイトルが既存のものと重複する場合
        if "title" in update_data and update_data["title"] != todo.title:
            existing = Todo.query.filter(
                Todo.title == update_data["title"],
                Todo.id != todo_id,
            ).first()
            if existing:
                msg = "同じタイトルのToDoアイテムが既に存在します"
                raise Conflict(msg)

        # 各フィールドを更新
        for key, value in update_data.items():
            if hasattr(todo, key):
                setattr(todo, key, value)

        db.session.commit()
        return todo

    @staticmethod
    def delete_todo(todo_id: int) -> None:
        """
        ToDoアイテムを削除する

        Args:
            todo_id: 削除するToDoのID

        Raises:
            NotFound: 指定されたIDのToDoが存在しない場合

        """
        todo = Todo.query.get(todo_id)
        if not todo:
            msg = f"ID {todo_id}のToDoは見つかりません"
            raise NotFound(msg)

        db.session.delete(todo)
        db.session.commit()
