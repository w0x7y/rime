-- Rime Aurora: Vivid neon accents on a darker background.
-- https://github.com/w0x7y/rime
hl.config({
    general = {
        col = { active_border = "rgb(4fa2ff)", inactive_border = "rgb(333842)", nogroup_border = "rgb(333842)", nogroup_border_active = "rgb(9b7dff)" },
    },
    group = {
        col = { border_active = "rgb(4fa2ff)", border_inactive = "rgb(333842)", border_locked_active = "rgb(e6f07c)", border_locked_inactive = "rgb(333842)" },
        groupbar = {
            text_color = "rgb(c8d2e2)",
            text_color_inactive = "rgb(6b768c)",
            col = { active = "rgb(4fa2ff)", inactive = "rgb(333842)", locked_active = "rgb(e6f07c)", locked_inactive = "rgb(333842)" },
        },
    },
    misc = { background_color = "rgb(1c1f25)" },
})
