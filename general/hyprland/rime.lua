-- Rime: Soft and muted pastels for long sessions.
-- https://github.com/w0x7y/rime
hl.config({
    general = {
        col = { active_border = "rgb(7aa4e4)", inactive_border = "rgb(3a404b)", nogroup_border = "rgb(3a404b)", nogroup_border_active = "rgb(bb98d6)" },
    },
    group = {
        col = { border_active = "rgb(7aa4e4)", border_inactive = "rgb(3a404b)", border_locked_active = "rgb(e4d098)", border_locked_inactive = "rgb(3a404b)" },
        groupbar = {
            text_color = "rgb(c3ccd9)",
            text_color_inactive = "rgb(6b768c)",
            col = { active = "rgb(7aa4e4)", inactive = "rgb(3a404b)", locked_active = "rgb(e4d098)", locked_inactive = "rgb(3a404b)" },
        },
    },
    misc = { background_color = "rgb(23272e)" },
})
