use crate::wall::*;

pub struct Room {
    pub walls: Vec<Wall>,
}

impl Room {
    pub fn new() -> Self {
        Self { walls: vec![] }
    }

    pub fn all_verts(&self) -> Vec<WallVertex> {
        self.walls.iter()
            .map(|w| w.vert_pos())
            .flatten()
            .collect::<Vec<WallVertex>>()
    }

    pub fn all_indices(&self) -> Vec<u16> {
        let mut indices: Vec<u16> = vec![];
        for (i, wall) in self.walls.iter().enumerate() {
            wall.indices().iter().for_each(|idc| indices.push(idc + (i as u16 * 4)));
        }

        indices
    }
}
