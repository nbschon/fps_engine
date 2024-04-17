use std::fs;
use std::io;

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
            .flat_map(|w| w.vert_pos())
            .collect::<Vec<WallVertex>>()
    }

    pub fn all_indices(&self) -> Vec<u16> {
        let mut indices: Vec<u16> = vec![];
        for (i, wall) in self.walls.iter().enumerate() {
            wall.indices().iter().for_each(|idc| indices.push(idc + (i as u16 * 4)));
        }

        indices
    }

    pub fn load_from_json(&mut self, path: String) -> io::Result<()> {
        let contents = fs::read_to_string(path).unwrap_or("".to_string());

        self.walls = serde_json::from_str(&contents)?;

        Ok(())
    }
}
