from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") # ham giup tach token tu header Authorization va tra ve token cho cac ham khac su dung


def get_current_user(
    token: str = Depends(oauth2_scheme), # Depends(oauth2_scheme) se tu dong lay token tu header Authorization va truyen vao tham so token
    db: Session = Depends(get_db), # Depends là hàm của FastAPI để khai báo phụ thuộc. Nó cho phép ta lấy các đối tượng hoặc giá trị từ các hàm khác mà không cần phải gọi chúng trực tiếp. Trong trường hợp này, nó sẽ tự động gọi hàm get_db() để lấy phiên làm việc cơ sở dữ liệu và truyền vào tham số db.
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user