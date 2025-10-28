#
# @pytest.mark.asyncio
# async def test_create_user(created_user: User) -> None:
#     created = created_user
#
#     assert isinstance(created, User)
#     assert created.id is not None
#     assert isinstance(created.created_at, datetime)
#     assert created.user_tg == 999
#     assert created.first_name == "Max"
#     assert created.last_name == "Test"
#     assert created.username == "test_user"
#
#
# def test_create_user_missing_fields() -> None:
#     with pytest.raises(ValidationError):
#         UserCreateSchema(**{})
#
#
# @pytest.mark.asyncio
# async def test_exists_user(
#     created_user: User,
#     instance: BaseCRUDManager[User],
# ) -> None:
#     user = created_user
#     exists = await instance.exist(field="id", value=user.id)
#
#     assert exists is not None
#
#
# @pytest.mark.asyncio
# async def test_get_one_user(
#     created_user: User,
#     instance: BaseCRUDManager[User],
# ) -> None:
#     get_user = await instance.get(user_tg=created_user.user_tg)
#     assert get_user is not None
#     assert get_user.id == created_user.id
#
#
# @pytest.fixture
# async def multiple_users(
#     db_session_maker: async_sessionmaker[AsyncSession],
# ) -> list[dict[str, Any]]:
#     users_data = [
#         {"user_tg": 1001, "first_name": "Alice", "last_name": "Smith"},
#         {"user_tg": 1002, "first_name": "Bob", "last_name": "Johnson"},
#         {"user_tg": 1003, "first_name": "Charlie", "last_name": "Brown"},
#         {"user_tg": 1004, "first_name": "David", "last_name": "Wilson"},
#         {"user_tg": 1005, "first_name": "Eve", "last_name": "Taylor"},
#     ]
#
#     async with db_session_maker() as session:
#         for data in users_data:
#             user = User(**data)
#             session.add(user)
#         await session.commit()
#
#     return users_data
#
#
# @pytest.mark.asyncio
# async def test_get_all_default_params(
#     multiple_users: list[dict[str, Any]],
#     instance: BaseCRUDManager[User],
# ) -> None:
#     users = await instance.get_all()
#     assert len(users) == 5
#
#
# @pytest.mark.asyncio
# async def test_get_all_pagination(
#     multiple_users: list[dict[str, Any]],
#     instance: BaseCRUDManager[User],
# ) -> None:
#     # Page 1
#     first_page = await instance.get_all(offset=0, limit=2)
#     assert len(first_page) == 2
#
#     # Page 2
#     second_page = await instance.get_all(offset=2, limit=2)
#     assert len(second_page) == 2
#
#     # Page 3
#     last_page = await instance.get_all(offset=4, limit=2)
#     assert len(last_page) == 1
#
#
# @pytest.mark.asyncio
# async def test_get_all_filters(
#     multiple_users: list[dict[str, Any]],
#     instance: BaseCRUDManager[User],
# ) -> None:
#     # Filter by first letter of last name
#     filtered = await instance.get_all(filters={"last_name": "Smith"})
#     assert len(filtered) == 1
#     assert filtered[0].last_name == "Smith"
#
#
# @pytest.mark.asyncio
# async def test_get_all_ordering(
#     multiple_users: list[dict[str, Any]],
#     instance: BaseCRUDManager[User],
# ) -> None:
#     # Order by last name ascending
#     ordered_asc = await instance.get_all(order_by=User.last_name.asc())
#     assert ordered_asc[0].last_name == "Brown"
#
#     # Order by last name descending
#     ordered_desc = await instance.get_all(order_by=User.last_name.desc())
#     assert ordered_desc[0].last_name == "Wilson"
#
#
# @pytest.mark.asyncio
# async def test_get_all_invalid_params(instance: BaseCRUDManager[User]) -> None:
#     with pytest.raises(ValueError):
#         await instance.get_all(offset=-1, limit=5)
#
#     with pytest.raises(ValueError):
#         await instance.get_all(offset=0, limit=0)
