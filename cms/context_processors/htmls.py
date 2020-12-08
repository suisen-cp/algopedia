def common_constants(request=None):
    context = {
        "htmls": {
            "tag": {
                "id": {
                    "select_button": "id_select_tag_button",
                    "input": "id_tag_input",
                    "selected_tags": "id_selected_tags",
                    "datalist": "id_tag_datalist",
                },
                "name": {
                    "deselect_button": "name_deselect_tag_button",
                    "selected_tags": "selected_tags",  # !
                }
            },
            "category": {
                "id": {
                    "input": "id_category_input",
                    "datalist": "id_category_datalist",
                },
            },
            "article": {
                "id": {
                    "form": "id_article_form"
                }
            },
            "search": {
                "id": {
                    "form": "id_search_form",
                    "search_or_order": "id_search_or_order",
                    "result": "id_search_result",
                },
            },
            "paging": {
                "name": {
                    "button": "name_paging_button",
                }
            },
            "fav": {
                "id": {
                    "info": "id_fav_info",
                    "toggle_button": "id_fav_toggle_button",
                },
            },
        },
    }
    return context
