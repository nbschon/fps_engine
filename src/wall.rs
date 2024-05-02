use cgmath::{Point3, Vector3, num_traits::WrappingAdd};
use rand::{Rng, thread_rng};
use serde::{Serialize, Deserialize};

#[repr(C)]
#[derive(Serialize, Deserialize, Debug, Copy, Clone)]
pub struct Wall {
    pub left_x: f32,
    pub left_z: f32,
    pub right_x: f32,
    pub right_z: f32,
    pub top: f32,
    pub bottom: f32,
}

#[repr(C)]
#[derive(Copy, Clone, Debug, bytemuck::Pod, bytemuck::Zeroable)]
pub struct WallVertex {
    position: [f32; 3],
    color: [f32; 3],
}

impl WallVertex {
    pub fn new(position: [f32; 3], color: [f32; 3]) -> Self {
        Self {
            position,
            color,
        }
    }

    pub fn desc() -> wgpu::VertexBufferLayout<'static> {
        wgpu::VertexBufferLayout {
            array_stride: std::mem::size_of::<WallVertex>() as wgpu::BufferAddress,
            step_mode: wgpu::VertexStepMode::Vertex,
            attributes: &[
                wgpu::VertexAttribute {
                    offset: 0,
                    shader_location: 0,
                    format: wgpu::VertexFormat::Float32x3,
                },
                wgpu::VertexAttribute {
                    offset: std::mem::size_of::<[f32; 3]>() as wgpu::BufferAddress,
                    shader_location: 1,
                    format: wgpu::VertexFormat::Float32x3,
                },
                wgpu::VertexAttribute {
                    offset: std::mem::size_of::<[f32; 3]>() as wgpu::BufferAddress,
                    shader_location: 2,
                    format: wgpu::VertexFormat::Float32x3,
                }
            ],
        }
    }
}

fn comp_to_srgb(comp: u8) -> f32 {
    ((comp as f32 / 255.0 + 0.055) / 1.055).powf(2.4)
}

fn hex_to_comp(color: u32) -> (u8, u8, u8) {
    let r = ((color & 0xFF0000) >> 16) as u8;
    let g = ((color & 0x00FF00) >> 8) as u8;
    let b = (color & 0x0000FF) as u8;
    (r, g, b)
}

pub fn hex_as_srgb(color: u32) -> [f32; 3] {
    let r = ((color & 0xFF0000) >> 16) as u8;
    let g = ((color & 0x00FF00) >> 8) as u8;
    let b = (color & 0x0000FF) as u8;
    let r_adj = comp_to_srgb(r);
    let g_adj = comp_to_srgb(g);
    let b_adj = comp_to_srgb(b);
    [r_adj, g_adj, b_adj]
}

pub fn jitter_color(color: u32, delta: Option<u8>) -> u32 {
    let (mut r, mut g, mut b) = hex_to_comp(color);
    let mut rng = thread_rng();
    let upper_range = delta.unwrap_or(15);
    let r_delta: u8 = rng.gen_range(0..upper_range);
    let g_delta: u8 = rng.gen_range(0..upper_range);
    let b_delta: u8 = rng.gen_range(0..upper_range);
    let r_add: bool = rng.gen::<bool>();
    let g_add: bool = rng.gen::<bool>();
    let b_add: bool = rng.gen::<bool>();

    if r_add { 
        r = r.saturating_add(r_delta);
    } else {
        r = r.wrapping_add((r_delta ^ 0xFF).wrapping_add(1));
    }

    if g_add { 
        g = g.saturating_add(g_delta);
    } else {
        g = g.wrapping_add((g_delta ^ 0xFF).wrapping_add(1));
    }

    if b_add { 
        b = b.saturating_add(b_delta);
    } else {
        b = b.wrapping_add((b_delta ^ 0xFF).wrapping_add(1));
    }

    (r as u32) << 16 | (g as u32) << 8 | b as u32
}

impl Wall {
    #[allow(dead_code)]
    pub fn new(l: (f32, f32), r: (f32, f32), t: f32, b: f32) -> Self {
        let (left_x, left_z) = l;
        let (right_x, right_z) = r;
        Self {
            left_x,
            left_z,
            right_x,
            right_z,
            top: t,
            bottom: b,
        }
    }

    #[rustfmt::skip]
    pub fn indices(&self) -> Vec<u16> {
        vec![
            0, 1, 3,
            1, 2, 3,
        ]
    }

    pub fn vert_pos(&self) -> Vec<WallVertex> {
        let top_left = [self.left_x, self.top, self.left_z];
        let bottom_left = [self.left_x, self.bottom, self.left_z];
        let bottom_right = [self.right_x, self.bottom, self.right_z];
        let top_right = [self.right_x, self.top, self.right_z];

        let cornflower_blue: u32 = 0x4287F5;

        let tl_vert = WallVertex::new(top_left, hex_as_srgb(jitter_color(cornflower_blue, None)));
        let bl_vert = WallVertex::new(bottom_left, hex_as_srgb(jitter_color(cornflower_blue, Some(25))));
        let br_vert = WallVertex::new(bottom_right, hex_as_srgb(jitter_color(cornflower_blue, None)));
        let tr_vert = WallVertex::new(top_right, hex_as_srgb(jitter_color(cornflower_blue, Some(25))));

        vec![tl_vert, bl_vert, br_vert, tr_vert]
    }
    
    pub fn get_normal(&self) -> Vector3<f32> {
        let top_left: Point3<f32> = [self.left_x, self.top, self.left_z].into();
        let bottom_left: Point3<f32> = [self.left_x, self.bottom, self.left_z].into();
        let top_right: Point3<f32>= [self.right_x, self.top, self.right_z].into();
    
        let pt_a = top_right - top_left;
        let pt_b = bottom_left - top_left;
        
        pt_a.cross(pt_b)
    }
    
    pub fn get_k(&self) -> f32 {
        let normal = self.get_normal();
        let pt: Point3<f32> = [self.left_x, self.top, self.left_z].into();
        (normal.x * pt.x) + (normal.y * pt.y) + (normal.z * pt.z)
    }

    pub fn get_coeffs(&self) -> (f32, f32, f32, f32) {
        let normal = self.get_normal();
        (normal.x, normal.y, normal.z, self.get_k())
    }
}
