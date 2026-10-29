-- Analisador de Partidas de CS2 - MVP 1
-- Regra de ouro: o banco guarda SOMENTE dados brutos.
-- K/D, KDA, HS%, ADR, KAST%, Win Rate etc. sao calculados depois (SQL/Python).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS player (
    player_id  INTEGER PRIMARY KEY,
    nickname   TEXT NOT NULL UNIQUE CHECK (length(trim(nickname)) > 0),
    steam_id   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS partida (
    partida_id         INTEGER PRIMARY KEY,
    data_partida       TEXT NOT NULL CHECK (data_partida GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    mapa               TEXT NOT NULL CHECK (length(trim(mapa)) > 0),
    resultado          TEXT NOT NULL CHECK (resultado IN ('vitoria', 'derrota', 'empate')),
    rounds_time        INTEGER NOT NULL CHECK (rounds_time >= 0),
    rounds_adversario  INTEGER NOT NULL CHECK (rounds_adversario >= 0),
    -- o resultado precisa bater com o placar
    CHECK (
        (resultado = 'vitoria' AND rounds_time >  rounds_adversario) OR
        (resultado = 'derrota' AND rounds_time <  rounds_adversario) OR
        (resultado = 'empate'  AND rounds_time =  rounds_adversario)
    )
);

CREATE TABLE IF NOT EXISTS performance (
    performance_id   INTEGER PRIMARY KEY,
    player_id        INTEGER NOT NULL REFERENCES player(player_id),
    partida_id       INTEGER NOT NULL REFERENCES partida(partida_id),

    -- combate
    kills            INTEGER NOT NULL CHECK (kills >= 0),
    deaths           INTEGER NOT NULL CHECK (deaths >= 0),
    assists          INTEGER NOT NULL CHECK (assists >= 0),
    headshots        INTEGER NOT NULL CHECK (headshots >= 0),
    damage           INTEGER NOT NULL CHECK (damage >= 0),

    -- utilitarios
    utility_damage   INTEGER NOT NULL CHECK (utility_damage >= 0),   -- DU
    enemies_blinded  INTEGER NOT NULL CHECK (enemies_blinded >= 0),  -- IC
    flash_assists    INTEGER NOT NULL CHECK (flash_assists >= 0),

    -- rounds e impacto
    rounds_played    INTEGER NOT NULL CHECK (rounds_played > 0),
    first_kills      INTEGER NOT NULL CHECK (first_kills >= 0),
    first_deaths     INTEGER NOT NULL CHECK (first_deaths >= 0),
    kast_rounds      INTEGER NOT NULL CHECK (kast_rounds >= 0),      -- rounds com Kill/Assist/Survive/Trade

    UNIQUE (player_id, partida_id),
    CHECK (headshots <= kills),
    CHECK (first_kills + first_deaths <= rounds_played),
    CHECK (kast_rounds <= rounds_played),
    CHECK (first_kills <= kills),
    CHECK (first_deaths <= deaths)
);

-- Regra entre tabelas (CHECK nao enxerga outra tabela): rounds_played = placar da partida
CREATE TRIGGER IF NOT EXISTS trg_performance_rounds_insert
BEFORE INSERT ON performance
BEGIN
    SELECT RAISE(ABORT, 'rounds_played difere do placar da partida')
    WHERE NEW.rounds_played <> (
        SELECT rounds_time + rounds_adversario FROM partida WHERE partida_id = NEW.partida_id
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_performance_rounds_update
BEFORE UPDATE OF rounds_played, partida_id ON performance
BEGIN
    SELECT RAISE(ABORT, 'rounds_played difere do placar da partida')
    WHERE NEW.rounds_played <> (
        SELECT rounds_time + rounds_adversario FROM partida WHERE partida_id = NEW.partida_id
    );
END;

-- Impede que o placar invalide performances existentes.
CREATE TRIGGER IF NOT EXISTS trg_partida_placar_update
BEFORE UPDATE OF rounds_time, rounds_adversario ON partida
WHEN EXISTS (
    SELECT 1 FROM performance
    WHERE performance.partida_id = OLD.partida_id
      AND performance.rounds_played <> (NEW.rounds_time + NEW.rounds_adversario)
)
BEGIN
    SELECT RAISE(ABORT, 'placar difere dos rounds_played registrados');
END;

CREATE TRIGGER IF NOT EXISTS trg_partida_data_insert
BEFORE INSERT ON partida
WHEN substr(NEW.data_partida, 1, 4) = '0000'
    OR COALESCE(
        strftime('%Y-%m-%d', NEW.data_partida, '+0 days') = NEW.data_partida,
        0
    ) = 0
BEGIN
    SELECT RAISE(ABORT, 'data_partida invalida');
END;

CREATE TRIGGER IF NOT EXISTS trg_partida_data_update
BEFORE UPDATE OF data_partida ON partida
WHEN substr(NEW.data_partida, 1, 4) = '0000'
    OR COALESCE(
        strftime('%Y-%m-%d', NEW.data_partida, '+0 days') = NEW.data_partida,
        0
    ) = 0
BEGIN
    SELECT RAISE(ABORT, 'data_partida invalida');
END;
