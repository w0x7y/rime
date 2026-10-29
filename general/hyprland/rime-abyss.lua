-- Rime Abyss: The coldest take, on a darker background: no yellow or orange anywhere, with rose as the only warm accent.
-- https://github.com/w0x7y/rime
hl.config({
    general = {
        col = { active_border = "rgb(6b9cf4)", inactive_border = "rgb(2c3039)", nogroup_border = "rgb(2c3039)", nogroup_border_active = "rgb(937ff2)" },
    },
    group = {
        col = { border_active = "rgb(6b9cf4)", border_inactive = "rgb(2c3039)", border_locked_active = "rgb(9cf0dc)", border_locked_inactive = "rgb(2c3039)" },
        groupbar = {
            text_color = "rgb(c2cde0)",
            text_color_inactive = "rgb(6b768c)",
            col = { active = "rgb(6b9cf4)", inactive = "rgb(2c3039)", locked_active = "rgb(9cf0dc)", locked_inactive = "rgb(2c3039)" },
        },
    },
    misc = { background_color = "rgb(15171c)" },
})
