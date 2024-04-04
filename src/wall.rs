pub struct Wall {
    pub left: (f32, f32),
    pub right: (f32, f32),
    pub top: f32,
    pub bottom: f32,
}

impl Wall {
    pub fn new(l: (f32, f32), r: (f32, f32), t: f32, b: f32) -> Self {
        Self {
            left: l,
            right: r,
            top: t,
            bottom: b,
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
        let bottom_right = [right_x, self.bottom, left_z];
        let top_right = [right_x, self.top, left_z];

        vec![top_left, bottom_left, bottom_right, top_right]
    }
}
