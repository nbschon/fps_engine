#[repr(C)]
pub struct Wall {
    pub left: (f32, f32),
    pub right: (f32, f32),
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
            ],
        }
    }
}

impl Wall {
    #[allow(dead_code)]
    pub fn new(l: (f32, f32), r: (f32, f32), t: f32, b: f32) -> Self {
        Self {
            left: l,
            right: r,
            top: t,
            bottom: b,
        }
    }

    pub fn desc() -> wgpu::VertexBufferLayout<'static> {
        wgpu::VertexBufferLayout {
            array_stride: std::mem::size_of::<[f32; 3]>() as wgpu::BufferAddress,
            step_mode: wgpu::VertexStepMode::Vertex,
            attributes: &[
                wgpu::VertexAttribute {
                    offset: 0,
                    shader_location: 0,
                    format: wgpu::VertexFormat::Float32x3,
                },
            ],
        }
    }

    pub fn indices(&self) -> Vec<u16> {
        vec![
            0, 1, 3,
            1, 2, 3,
        ]
    }

    pub fn vert_pos(&self) -> Vec<WallVertex> {
        let (left_x, left_z) = self.left;
        let (right_x, right_z) = self.right;

        let top_left = [left_x, self.top, left_z];
        let bottom_left = [left_x, self.bottom, left_z];
        let bottom_right = [right_x, self.bottom, right_z];
        let top_right = [right_x, self.top, right_z];
        let tl_vert = WallVertex::new(top_left, [1.0, 0.0, 0.0]);
        let bl_vert = WallVertex::new(bottom_left, [0.0, 1.0, 0.0]);
        let br_vert = WallVertex::new(bottom_right, [0.0, 0.0, 1.0]);
        let tr_vert = WallVertex::new(top_right, [1.0, 1.0, 0.0]);

        vec![tl_vert, bl_vert, br_vert, tr_vert]
    }
}
