from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

usuario_admin = {"username": "admin", "password": "ozzy123"}

# Configurando o JWT
SECRET_KEY = "essa_chave_deveria_ser_muito_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Token de autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def authenticate_user(username: str, password: str):
    """
    Autentica o usuário verificando o nome de usuário e a senha.
    """
    if username == usuario_admin["username"] and password == usuario_admin["password"]:
        return usuario_admin
    return None


# Criar o token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Cria um token JWT com os dados fornecidos e uma data de expiração opcional.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para autenticar o usuário e retornar um token JWT.
    """

    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Usuário/senha inválidos")

    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Obtém o usuário atual a partir do token JWT.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    return username


@router.post("/refresh")
def refresh_token(current_user: str = Depends(get_current_user)):
    """
    Endpoint para dar um refresh no token JWT
    É necessário que o token atual ainda esteja válido
    """
    new_token = create_access_token(
        data={"sub": current_user},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": new_token, "token_type": "bearer"}
