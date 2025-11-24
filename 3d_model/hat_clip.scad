thickness = 3;

width = 120;

bar_height = 80;
bar_width = 10;

$fn = 80;

module 2d_shape() {
union() {
    // 横梁
    translate([0, 0, 0]) {
        square([width, 15]);
    }
    
    // 左柱
    translate([0, 0, 0]) {
        rotate([0, 0, 0]) {
            square([bar_width, bar_height]);
        }
    }
    
    // 右柱
    translate([width-bar_width, 0, 0]) {
        rotate([0, 0, 0]) {
            square([bar_width, bar_height]);
        }
    }
    
    // 中间竖柱
    translate([width/2-bar_width, 0, 0]){
        square([bar_width*2, bar_height]);
    }
    
    //延伸柱
    extra_length = 5;
    translate([width/2-bar_width, -extra_length, 0]){
        square([bar_width*2, extra_length]);
    }
    
    // 树莓派连接板
    offset = 15;
    rpi_width = 85 + offset;
    rpi_height = 55 + offset/2;
    translate([width/2-rpi_width/2, -rpi_height-extra_length, 0]){   
        difference() {
            square([rpi_width, rpi_height]);
            
            // Space
            translate([rpi_width/2-80/2,rpi_height/2-35/2,0]) square([80, 35]);
            
            // 螺丝孔
            x=3.5 + offset/2;
            y=3.5 + offset/2/2;
            w = 58;
            h = 49;
            translate([x,y,0]) screw_hole();
            translate([x+w,y,0]) screw_hole();
            translate([x,y+h,0]) screw_hole();
            translate([x+w,y+h,0]) screw_hole();
    }

    }
    
    // 三角板
    translate([40, 30, 0]) rotate([0, 0, 90]) pentagon();
    translate([80, 30, 0]) rotate([0, 180, 270]) pentagon();
}
}

module screw_hole(diameter=3, length = 6) {
        union(){
            circle(d=diameter);
            translate([diameter, 0, 0]) {
                circle(d=diameter);
            }
            translate([0, -diameter/2, 0]) {
                square([length-diameter, diameter], false);
            }
        }
    }

// 支撑三角板
module pentagon() {
    
    translate([0, 0, 0]) {
        square([60, bar_width]);
    }
    translate([70, 0, 0]) {
        rotate([0, 0, 90]) square([40, bar_width]);
    }
    translate([70, 40, 0]) {
        rotate([0, 0, 135]) square([40, bar_width]);
    }
}

module 3d_shape() {
linear_extrude(
    height = thickness,        // 拉伸高度
    center = false,      // 是否居中（默认false）
    convexity = 10,     // 渲染质量（通常用10）
    twist = 0,          // 扭曲角度（度）
    slices = 20         // 切片数量（影响扭曲质量）
) {
    2d_shape();
}
}

3d_shape();