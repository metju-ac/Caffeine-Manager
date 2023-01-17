from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from typing import Optional, Union
from config import *
from responses import *
from tools import *
from caffeine_model import *

app = Flask(__name__)
app.config.from_object(DbConfig)

db = SQLAlchemy(app)


class User(db.Model):
    """
    A class to represent user.

    Attributes
    ----------
    id: int
        user's unique id
    login: str
        user's unique login
    password: str
        user's password
    email: str
        user's unique email
    """
    __tablename__ = "users"
    id: int = db.Column(db.Integer, primary_key=True)
    login: str = db.Column(db.String(100), nullable=False)
    password: str = db.Column(db.String(100), nullable=False)
    email: str = db.Column(db.String(100), nullable=False)

    def __init__(self, login: str, password: str, email: str) -> None:
        """
        Constructs new User object.

        Parameters
        ----------
        login: str
            user's unique login
        password: str
            user's password
        email: str
            user's unique email
        """
        self.login = login
        self.password = password
        self.email = email

    def __str__(self) -> str:
        return f'User with id set to: {self.id}, login to: {self.login}, ' \
               f'password to: {self.password} ' f'and email to: {self.email}'

    def __repr__(self) -> str:
        return f'User(id={self.id}, login={self.login}, password={self.password}, email={self.email})'


class Machine(db.Model):
    """
    A class to represent machine.

    Attributes
    ----------
    id: int
        machine's unique id
    """
    __tablename__ = "machines"
    id: int = db.Column(db.Integer, primary_key=True)

    __mapper_arg__ = {'polymorphic_identity': 'machine'}

    def __init__(self) -> None:
        """
        Constructs new Machine object.
        """
        pass

    def __str__(self) -> str:
        return f'Machine with id set to: {self.id}'

    def __repr__(self) -> str:
        return f'Machine(id={self.id})'


class CoffeeMachine(Machine):
    """
    A class to represent coffee machine.

    Attributes
    ----------
    id: int
        coffee machine's unique id
    name: str
        coffee machine's name
    caffeine: int
        coffee machine's caffeine value in mg per cup
    """
    __tablename__ = "coffee_machines"
    id: int = db.Column(db.Integer, db.ForeignKey("machines.id"), primary_key=True)
    name: str = db.Column(db.String(100))
    caffeine: int = db.Column(db.Integer)

    __mapper_args__ = dict(
        polymorphic_identity='coffee_machine',
        inherit_condition=(id == Machine.id)
    )

    def __init__(self, name: str, caffeine: int) -> None:
        """
        Constructs new CoffeeMachine object.

        Parameters
        ----------
        name: str
            coffee machine's name
        caffeine: int
            coffee machine's caffeine value in mg per cup
        """
        Machine.__init__(self)
        self.name = name
        self.caffeine = caffeine

    def __str__(self) -> str:
        return f'CoffeeMachine with id set to: {self.id}, name to {self.name} and caffeine to {self.caffeine}'

    def __repr__(self) -> str:
        return f'CoffeeMachine(id={self.id}, name={self.name}, caffeine={self.caffeine})'


class CoffeePurchase(db.Model):
    """
    A class to represent coffee purchase.

    Attributes
    ----------
    id: int
        coffee purchase's unique id
    user_id: int
        id of user that bought the coffee
    machine_id: int
        id of coffee machine from which was the coffee bought
    timestamp: datetime
        time of the purchase
    caffeine: int
        how much caffeine does the bought coffee contain
        (coffee machine can be adjusted, that is why I store it here as well)
    """
    __tablename__ = "coffee_purchases"
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("users.id"))
    machine_id: int = db.Column(db.Integer, db.ForeignKey("machines.id"))
    timestamp: datetime = db.Column(db.TIMESTAMP)
    caffeine: int = db.Column(db.Integer)

    def __init__(self, user_id: int, machine_id: int, timestamp: datetime, caffeine: int) -> None:
        """
        Constructs new CoffeePurchase object.

        Parameters
        ----------
        user_id: int
            id of user that bought the coffee
        machine_id: int
            id of coffee machine from which was the coffee bought
        timestamp: datetime
            time of the purchase
        caffeine: int
            how much caffeine does the bought coffee contain
            (coffee machine can be adjusted, that is why I store it here as well)
        """
        self.user_id = user_id
        self.machine_id = machine_id
        self.timestamp = timestamp
        self.caffeine = caffeine

    def __str__(self) -> str:
        return f'CoffeePurchase with id set to: {self.id}, user_id to: {self.user_id}, ' \
               f'machine_id to: {self.machine_id}, timestamp to: {self.timestamp} and caffeine to: {self.caffeine}'

    def __repr__(self) -> str:
        return f'CoffeePurchase(id={self.id}, user_id={self.user_id}, machine_id={self.machine_id}, ' \
               f'timestamp={self.timestamp}, caffeine={self.caffein_mg})'


def create_user(login: str, password: str, email: str) -> Optional[int]:
    """
    Tries to create new User object.

    Parameters
    ----------
    login: str
        new user's login
    password: str
        new user's password
    email: str
        new user's email

    Returns
    -------
    new user's id: int
        None in case of internal database error
        -1 if there already is user with given login
        -2 if there already is user with given email
        positive id of created user else

    """
    existing: Optional[User] = User.query.filter_by(login=login).first()
    if existing is not None:
        return -1
    existing = User.query.filter_by(email=email).first()
    if existing is not None:
        return -2

    new_user: User = User(login, password, email)

    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user.id
    except:
        db.session.rollback()
        return None


def create_coffee_machine(name: str, caffeine: int) -> Optional[int]:
    """
    Tries to create new CoffeeMachine object.

    Parameters
    ----------
    name: str
        new coffee machine's name
    caffeine: int
        new coffee machine's caffeine value in mg per cup

    Returns
    -------
    new coffee machine's id: int
        None in case of internal database error
        positive id of created coffee machine else
    """
    new_coffee_machine: CoffeeMachine = CoffeeMachine(name, caffeine)

    try:
        db.session.add(new_coffee_machine)
        db.session.commit()
        return new_coffee_machine.id
    except:
        db.session.rollback()
        return None


def create_coffee_purchase(user_id: int, machine_id: int, timestamp: datetime) -> Optional[int]:
    """
    Tries to create new CoffeePurchase object.

    Parameters
    ----------
    user_id: int
        id of user who bought the coffee
    machine_id: int
        id of coffee machine from which was the coffee bought
    timestamp: datetime
        time of the purchase

    Returns
    -------
    new coffee purchase's id: int
        None in case of internal database error
        -1 if there is no user with given id
        -2 if there is no machine with given id
        positive id of created coffee machine else
    """
    user: Optional[User] = User.query.filter_by(id=user_id).first()
    if user is None:
        return -1

    machine: Optional[CoffeeMachine] = CoffeeMachine.query.filter_by(id=machine_id).first()
    if machine is None:
        return -2

    new_coffee_purchase: CoffeePurchase = CoffeePurchase(user_id, machine_id, timestamp, machine.caffeine)

    try:
        db.session.add(new_coffee_purchase)
        db.session.commit()
        return new_coffee_purchase.id
    except:
        db.session.rollback()
        return None


def register_purchase(user_id: int, machine_id: int, timestamp: datetime) -> Union[int, Dict[str, Optional[int]]]:
    """
    Handles creation of new CoffeePurchase object

    Parameters
    ----------
    user_id: int
        id of user who bought the coffee
    machine_id: int
        id of coffee machine from which was the coffee bought
    timestamp: datetime
        time of the purchase

    Returns
    -------
    response: JSON object
        containing either new coffee purchase's id or error code and error text
    """
    created_purchase_id: Optional[int] = create_coffee_purchase(user_id, machine_id, timestamp)

    if created_purchase_id == -1:
        return conflict_response_missing_referenced_object("User", user_id)
    elif created_purchase_id == -2:
        return conflict_response_missing_referenced_object("CoffeeMachine", machine_id)

    return {"coffee_purchase_id": created_purchase_id}


# PUT /user/request
@app.route("/user/request", methods=["PUT"])
def create_new_user():
    request_data = request.get_json()
    if not validate_json_arguments(request_data, ["login", "password", "email"]):
        return missing_arguments_response()

    login: str = request_data["login"]
    password: str = request_data["password"]
    email: str = request_data["email"]

    for key, value in {"login": login, "password": password, "email": email}.items():
        if not check_string(value):
            return invalid_argument_response(key)

    created_user_id: Optional[int] = create_user(login, password, email)

    # Should also handle problems with database, something like this. Same for other requests
    # if created_coffee_machine_id is None:
    #     return 500

    if created_user_id == -1:
        return conflict_response_non_unique_argument("User", "login")
    elif created_user_id == -2:
        return conflict_response_non_unique_argument("User", "email")

    return {"user_id": created_user_id}


# POST /machine
@app.route("/machine", methods=["POST"])
def register_machine():
    request_data = request.get_json()
    if not validate_json_arguments(request_data, ["name", "caffeine"]):
        return missing_arguments_response()

    name: str = request_data["name"]
    caffeine: int = request_data["caffeine"]

    created_coffee_machine_id: Optional[int] = create_coffee_machine(name, caffeine)

    return {"coffee_machine_id": created_coffee_machine_id}


# GET /coffee/buy/:user-id/:machine-id
@app.route("/coffee/buy/<int:user_id>/<int:machine_id>", methods=["GET"])
def register_purchase_get(user_id: int, machine_id: int):
    return register_purchase(user_id, machine_id, datetime.now())


# PUT /coffee/buy/:user-id/:machine
@app.route("/coffee/buy/<int:user_id>/<int:machine_id>", methods=["PUT"])
def register_purchase_put(user_id: int, machine_id: int):
    request_data = request.get_json()
    if not validate_json_arguments(request_data, ["timestamp"]):
        return missing_arguments_response()

    timestamp: str = request_data["timestamp"]

    return register_purchase(user_id, machine_id, datetime.fromisoformat(timestamp))


# GET /stats/coffee
@app.route("/stats/coffee", methods=["GET"])
def stats_all():
    return stats_coffee_query_to_list(CoffeePurchase.query.all())


# GET /stats/coffee/machine/:id
@app.route("/stats/coffee/machine/<int:machine_id>", methods=["GET"])
def stats_by_machine(machine_id: int):
    machine: Optional[CoffeeMachine] = CoffeeMachine.query.filter_by(id=machine_id).first()
    if machine is None:
        return conflict_response_missing_referenced_object("Machine", machine_id)

    return stats_coffee_query_to_list(CoffeePurchase.query.filter_by(machine_id=machine_id).all())


# GET /stats/coffee/user/:id
@app.route("/stats/coffee/user/<int:user_id>", methods=["GET"])
def stats_by_user(user_id: int):
    user: Optional[User] = User.query.filter_by(id=user_id).first()
    if user is None:
        return conflict_response_missing_referenced_object("User", user_id)

    return stats_coffee_query_to_list(CoffeePurchase.query.filter_by(user_id=user_id).all())


# GET /stats/level/user/:id
@app.route("/stats/level/user/<int:user_id>", methods=["GET"])
def stats_level(user_id: int):
    user: Optional[User] = User.query.filter_by(id=user_id).first()
    if user is None:
        return conflict_response_missing_referenced_object("User", user_id)

    purchases: List[Tuple[int, datetime]] = []
    query_purchases: List[CoffeePurchase] = CoffeePurchase.query.filter_by(user_id=user_id).all()
    for purchase in query_purchases:
        purchases.append((purchase.caffeine, purchase.timestamp))

    return compute_caffeine_level(purchases)


if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        db.create_all()
    app.run(debug=True)
