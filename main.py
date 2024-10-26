from flask import Flask, redirect, url_for, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from typing import Optional


ROLE_ADMIN = 0
ROLE_BIDDER = 1
ROLE_SELLER = 2

class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite+pysqlite:///:memory:"
app.config["SECRET_KEY"] = "egwiue27r82upg2ioefe9pp2u3u7rg92foe"

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'User'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    userrole: Mapped[int] = mapped_column(nullable=False)

class Auction(db.Model):
    __tablename__ = 'Auction'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column()
    bidding: Mapped[int] = mapped_column(nullable=False, default=0)

    bidder_id: Mapped[Optional[int]] = mapped_column(ForeignKey('User.id'))
    bidder: Mapped[Optional[User]] = relationship(foreign_keys=[bidder_id])

    seller_id: Mapped[int] = mapped_column(ForeignKey('User.id'))
    seller: Mapped[User] = relationship(foreign_keys=[seller_id])


with app.app_context():
    db.create_all()
    # db.session.add(Auction(title="Testing auction 1", description="Testing auction 1 description"))
    db.session.commit()

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/search/<item_name>")
def search(item_name):
    return f'searching {item_name}'

@app.route("/auction/<int:auction_id>")
def page_auction(auction_id):
    auction = db.session.execute(db.select(Auction).where(Auction.id == auction_id)).scalar()
    if auction is not None:
        return render_template("auction.html", auction=auction)
    else:
        abort(404, "There is no such auction")

@app.route('/auction/search')
def page_search():
    query = request.args.get('query')
    if query is None:
        return render_template('auction-search.html', auctions=Auction.query.order_by(Auction.title).all())
    else:
        auctions = Auction.query.filter(Auction.title.contains(query)).all()
        return render_template('auction-search.html', auctions=auctions)

@app.route("/auction/add")
def auction_add():
    return render_template("auction-add.html")

@app.route("/api/auction/add", methods=['POST'])
def api_auction_add():
    if not (current_user.is_authenticated and current_user.userrole == 2):
        abort(400, "Not a seller")

    auction = Auction(title=request.form.get('title'), description=request.form.get('description'), seller_id=current_user.id)
    db.session.add(auction)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/api/auction/bid', methods=['POST'])
def api_auction_bid():
    if not (current_user.is_authenticated and current_user.userrole == 1):
        abort(400, "Not a bidder")

    auction_id = request.form.get('auction-id', type=int)
    auction = Auction.query.filter_by(id=auction_id).first()
    if auction is None:
        abort(400, 'No auction')

    bidding = request.form.get('bidding', type=int)
    bidder = current_user.id

    if auction.bidding < bidding:
        auction.bidding = bidding
        auction.bidder_id = bidder

        db.session.commit()

    if current_user.is_authenticated:
        return redirect(url_for('page_auction', auction_id=auction_id))
    else:
        abort(400, 'User not logged in')

@app.route('/api/register', methods=['POST'])
def api_register():
    user = User(username=request.form.get('username'),
                password=request.form.get('password'),
                userrole=request.form.get('userrole'))
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("page_login"))

@app.route("/register")
def page_register():
    return render_template('register.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    user = User.query.filter_by(username=request.form.get('username')).first()
    if user is not None and user.password == request.form.get('password'):
        login_user(user)
        return redirect(url_for('home'))
    return redirect(url_for('page_login'))

@app.route('/login')
def page_login():
    return render_template('login.html')

@app.route('/logout')
def page_logout():
    logout_user()
    return redirect(url_for('home'))
