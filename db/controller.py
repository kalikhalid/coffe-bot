from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .db import History, Addresses, AdminInfo, Items, Orders, Base
from typing import Dict, Tuple, List, Optional
from sqlalchemy import select, update, insert, or_
from sqlalchemy.sql.expression import func


class DbController:
    Base()

    def __init__(self, connection_string: str) -> None:
        self.engine = create_engine(connection_string, echo=True)
        self.session = sessionmaker(autoflush=False, bind=self.engine)

    def new_order(self, order_data: Dict[str, str], user_id: int) -> Tuple[int, int]:
        """
        Helper func for creating new order and returning this order id and order address id
        """
        with self.session.begin() as session:
            query = select(Addresses.__table__).where(
                Addresses.address == order_data["adress"]
            )
            curent_adress_id = session.execute(query).fetchall()[0][0]
            new_order = Orders(
                user_id=user_id,
                ordr=order_data["order"],
                address_id=curent_adress_id,
                is_complete=False,
            )
            session.add(new_order)
            session.commit()
        with self.session.begin() as session:
            query = (
                select(Orders.ord_id)
                .where(
                    Orders.user_id == user_id,
                    Orders.ordr == order_data["order"],
                    Orders.address_id == curent_adress_id,
                    Orders.is_complete == False,
                )
                .order_by(Orders.ord_id.desc())
            )
            order_id = session.execute(query).first().ord_id
            session.execute(query)
            session.commit()
            return order_id, curent_adress_id

    def make_order(self, user_id: int, order_data: Dict[str, str]) -> Tuple[int, List]:
        """
        Main function to creting order
        """
        with self.session.begin() as session:
            order_id, curent_adress_id = self.new_order(order_data, user_id)
            additional_query = select(AdminInfo.__table__).where(
                AdminInfo.address_id == curent_adress_id
            )
            admins_list = session.execute(additional_query).fetchall()
            result = (order_id, [i[0] for i in admins_list])
            session.commit()
            return result

    def db_add_admin(self, msgtext: str, msgchatid: int) -> bool:
        """
        Adding new admin by telegram chat id
        """
        with self.session.begin() as session:
            query = select(AdminInfo.telegram_id)
            print(session.execute(query).fetchall())
            if (msgchatid,) not in session.execute(query).fetchall():
                return False

            data = msgtext.split("/addadmin")[1].split()
            if len(data) < 2:
                return False
            query = insert(AdminInfo).values(telegram_id=data[0], address_id=data[1])
            session.execute(query)
            session.commit()
            return True

    def check_user(self, chat_id: int) -> bool:
        """
        Сhecking user for administrator by telegram chat id
        """
        with self.session.begin() as session:
            admin_ids = [
                i[0] for i in session.execute(select(AdminInfo.telegram_id)).fetchall()
            ]
            if chat_id not in admin_ids:
                return False
            return True

    def get_menu(self) -> str:
        with self.session.begin() as session:
            menu = session.execute(select(Items.name)).fetchall()
            return " ".join(i[0] for i in menu)

    def get_history_by_id(self, id: int):
        """
        getting histroy by telegram chat id
        """
        with self.session.begin() as session:
            history = session.execute(
                select(History.ordr).where(History.id == id)
            ).fetchall()
            msg = []
            for i in enumerate(history[-10:]):
                msg.append("order {}\n".format(i[0] + 1) + i[1][0] + "\n")
            return (
                "".join(i for i in msg)
                if len(msg) > 0
                else "Истории пока нет! Сделайте заказ и онa сразу появится!"
            )

    def get_high(self) -> str:
        """
        Getting most ordering menu item
        """
        with self.session.begin() as session:
            return session.execute(select(Items.name, func.max(Items.top))).fetchall()[
                0
            ][0]

    def add_to_history(self, web_app_data: str, id: int):
        """
        Adding order to history and returning this order as str
        """
        with self.session.begin() as session:
            conditions = [Items.id == int(i) for i in web_app_data.split()]
            query = select(Items.__table__).where(or_(*conditions))
            items = session.execute(query).mappings().fetchall()
            order = "".join([str(i["name"]) + "\n" for i in items])
            new_order = History(ordr=order, id=id)
            session.add(new_order)
            for i in items:
                stmt = update(Items).where(Items.id == i["id"]).values(top=i["top"] + 1)
                session.execute(stmt)
            session.commit()
            return order

    def get_addresses(self) -> str:
        """
        Getting addresses and id from datebase
        """
        with self.session.begin() as session:
            addresses = session.execute(select(Addresses.__table__)).fetchall()
            msg = "\n".join(f"{i[0]} - {i[1]}" for i in addresses)
            return msg

    def get_user_id_by_order_id(self, order_id: int) -> Optional[int]:
        with self.session.begin() as session:
            user_id = session.execute(
                select(Orders.user_id).where(Orders.ord_id == order_id)
            ).fetchall()
            return user_id[0][0] if len(user_id) >= 1 else None

    def complite_order(self, order_id: str) -> None:
        """
        mark the order as completed
        """
        with self.session.begin() as session:
            query = (
                update(Orders).where(Orders.ord_id == order_id).values(is_complete=True)
            )
            session.execute(query)
            session.commit()
