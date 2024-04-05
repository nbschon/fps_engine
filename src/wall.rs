#[repr(C)]
pub struct Wall {
    pub left: (f32, f32),
    pub right: (f32, f32),
    pub top: f32,
    pub bottom: f32,
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

    pub fn vert_pos(&self) -> Vec<[f32; 3]> {
        let (left_x, left_z) = self.left;
        let (right_x, right_z) = self.right;

        let top_left = [left_x, self.top, left_z];
        let bottom_left = [left_x, self.bottom, left_z];
        let bottom_right = [right_x, self.bottom, right_z];
        let top_right = [right_x, self.top, right_z];

        vec![top_left, bottom_left, bottom_right, top_right]
    }
}
