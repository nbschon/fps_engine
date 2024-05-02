use std::fs;
use std::io;
use cgmath::Point3;
use serde::Deserialize;

use crate::wall::*;

#[derive(Deserialize)]
pub struct Level {
    pub walls: Vec<Wall>,
    points: Vec<(f32, f32)>,
    scale_factor: f32,
    #[serde(default)]
    top_left: (f32, f32),
    #[serde(default)]
    bottom_left: (f32, f32),
    #[serde(default)]
    bottom_right: (f32, f32),
    #[serde(default)]
    top_right: (f32, f32),
    pub start_pos: (f32, f32),
}

impl Level {
    pub fn all_verts(&self) -> Vec<WallVertex> {
        let mut walls = self.walls.iter()
            .flat_map(|w| w.vert_pos())
            .collect::<Vec<WallVertex>>();

        let floor_tr = WallVertex::new([self.top_right.0, 0.0, self.top_right.1], hex_as_srgb(0x60996F));
        let floor_br = WallVertex::new([self.bottom_right.0, 0.0, self.bottom_right.1], hex_as_srgb(0x457A53));
        let floor_bl = WallVertex::new([self.bottom_left.0, 0.0, self.bottom_left.1], hex_as_srgb(0x60996F));
        let floor_tl = WallVertex::new([self.top_left.0, 0.0, self.top_left.1], hex_as_srgb(0x72B584));

        walls.extend_from_slice(&[floor_tr, floor_br, floor_bl, floor_tl]);

        walls
    }

    pub fn all_indices(&self) -> Vec<u16> {
        let mut indices: Vec<u16> = vec![];
        for (i, wall) in self.walls.iter().enumerate() {
            wall.indices()
                .iter()
                .for_each(|idc| indices.push(idc + (i as u16 * 4)));
        }

        let start_idx = *indices.last().unwrap_or(&0);
        let floor_idxs = [
            0, 1, 3,
            1, 2, 3,
        ];
        floor_idxs.iter().for_each(|idc| indices.push(idc + start_idx + 1));

        indices
    }
    
    pub fn closest_walls(&self, pt: Point3<f32>) -> Vec<Wall> {
        let mut idx_by_dist = self.walls.iter().enumerate().map(|(idx, wall)| {
            let x = (wall.right_x + wall.left_x) / 2.0;
            // let y = (w.top + w.bottom) / 2.0;
            let z = (wall.right_z + wall.left_z) / 2.0;
            let cam_x = pt.x;
            // let cam_y = pt.y;
            let cam_z = pt.z;

            // let dist = (cam_x - x).powf(2.0) + (cam_y - y).powf(2.0) + (cam_z - z).powf(2.0);
            let dist = (cam_x - x).powf(2.0) + (cam_z - z).powf(2.0);
            (idx, dist)
        }).collect::<Vec<(usize, f32)>>();
        
        idx_by_dist.sort_by(|x, y| {
            let (_, dist_1) = x;
            let (_, dist_2) = y;
            dist_1.partial_cmp(dist_2).unwrap()
        });
        
        let walls_by_idx = idx_by_dist.iter().map(|(idx, _)| {
            self.walls[*idx]
        }).collect::<Vec<Wall>>();
        walls_by_idx[..3].to_vec()
    }
}

pub fn load_from_json(path: String) -> io::Result<Level> {
    let contents = fs::read_to_string(path).unwrap_or("".to_string());
    let mut level: Level = serde_json::from_str(&contents)?;

    let mut min_x: f32 = 0.0;
    let mut min_z: f32 = 0.0;
    let mut max_x: f32 = 0.0;
    let mut max_z: f32 = 0.0;

    for pt in &level.points {
        let (pt_x, pt_z) = *pt;
        if pt_x < min_x {
            min_x = pt_x
        } else if pt_x > max_x {
            max_x = pt_x
        }

        if pt_z < min_z {
            min_z = pt_z
        } else if pt_z > max_z {
            max_z = pt_z
        }
    }

    level.top_left = (min_x, max_z);
    level.bottom_left = (min_x, min_z);
    level.bottom_right = (max_x, min_z);
    level.top_right = (max_x, max_z);

    Ok(level)
}
