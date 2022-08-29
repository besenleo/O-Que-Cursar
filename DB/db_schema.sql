create table if not exists usuario(
    -- Essa tabela armazena os dados dos usuarios
    id_user          integer unique not null,
    nome             varchar(50)    not null,
    email            varchar(50)    not null,
    senha            varchar(30)    not null, -- TODO: Senhas nao devem ser armazenadas em plain text no database
    status_perfil    boolean        not null,
    constraint pk_aluno primary key(id_user)
);

---------------------------------------------------------------

create table if not exists professor(
    -- Essa tabela armazena os dados dos professores
    id_prof          integer unique not null,
    titulo           varchar(30)    not null,
    constraint pk_professor primary key(id_prof),
    constraint fk_professor_usuario foreign key (id_prof) references usuario(id_user) on delete cascade
);

---------------------------------------------------------------

create table if not exists curso(
    -- Essa tabela armazena os dados dos cursos
    id_curso        integer unique not null,
    nome            varchar(50)    not null,
    descricao       varchar(300)   not null,
    periodo         varchar(10)    not null,
    tipoCurso       varchar(15)    not null,
    disponivel      boolean        not null,
    constraint pk_curso primary key(id_curso)
);

---------------------------------------------------------------

create table if not exists post(
    -- Essa tabela armazena os dados das postagens
    id_post         integer unique not null,
    conteudo        varchar(560)   not null,
    data_criacao    date           not null,
    id_curso        integer        not null,
    id_prof         integer        not null,
    constraint pk_post primary key(id_post),
    constraint fk_post_curso foreign key(id_curso) references curso(id_curso) on delete cascade,
    constraint fk_post_professor foreign key(id_prof) references professor(id_prof) on delete cascade
);

---------------------------------------------------------------

create table if not exists comentario(
    -- Essa tabela armazena os dados dos comentarios das postagens
    id_comentario   integer unique not null,
    conteudo        varchar(280)   not null,
    data_criacao    date           not null,
    id_post         integer        not null,
    id_usuario      integer        not null,
    constraint pk_comentario primary key(id_comentario),
    constraint fk_comentario_post foreign key(id_post) references post(id_post) on delete cascade,
    constraint fk_comentario_usuario foreign key(id_usuario) references usuario(id_user) on delete cascade
);
