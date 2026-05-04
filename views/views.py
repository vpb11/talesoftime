#thin routes that call services and pass viewmodels to templates, no business logic

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.services import (
    CharacterService, ItemService, QuestService,
    InventoryService, QuestProgressService, DashboardService,
    RewardService, QuestRewardService,
)

bp = Blueprint("main", __name__)

#new service instance per request
def _char_svc():   return CharacterService()
def _item_svc():   return ItemService()
def _quest_svc():  return QuestService()
def _inv_svc():    return InventoryService()
def _qp_svc():     return QuestProgressService()
def _dash_svc():   return DashboardService()
def _reward_svc(): return RewardService()
def _qr_svc():     return QuestRewardService()


#Dashboard

@bp.route("/")
def dashboard():
    vm = _dash_svc().get_dashboard()
    return render_template("dashboard.html", vm=vm)


#Characters

@bp.route("/characters")
def character_list():
    vm = _char_svc().list_characters()
    return render_template("characters/list.html", vm=vm)


@bp.route("/characters/new", methods=["GET", "POST"])
def character_create():
    svc = _char_svc()
    if request.method == "POST":
        data = {
            "CharacterName": request.form["CharacterName"],
            "ClassID":       int(request.form["ClassID"]),
            "SpeciesID":     int(request.form["SpeciesID"]),
            "AlignmentID":   int(request.form["AlignmentID"]),
            "Level":         int(request.form.get("Level", 1)),
        }
        svc.create_character(data)
        flash("Character created successfully.", "success")
        return redirect(url_for("main.character_list"))
    form_vm = svc.get_form_data()
    return render_template("characters/form.html", form_vm=form_vm, action="Create")


@bp.route("/characters/<int:character_id>/edit", methods=["GET", "POST"])
def character_edit(character_id):
    svc = _char_svc()
    if request.method == "POST":
        data = {
            "CharacterName": request.form["CharacterName"],
            "ClassID":       int(request.form["ClassID"]),
            "SpeciesID":     int(request.form["SpeciesID"]),
            "AlignmentID":   int(request.form["AlignmentID"]),
            "Level":         int(request.form.get("Level", 1)),
        }
        svc.update_character(character_id, data)
        flash("Character updated.", "success")
        return redirect(url_for("main.character_list"))
    form_vm = svc.get_form_data(character_id)
    return render_template("characters/form.html", form_vm=form_vm, action="Edit")


@bp.route("/characters/<int:character_id>/delete", methods=["POST"])
def character_delete(character_id):
    _char_svc().delete_character(character_id)
    flash("Character deleted.", "warning")
    return redirect(url_for("main.character_list"))


@bp.route("/characters/<int:character_id>/inventory")
def character_inventory(character_id):
    char_vm = _char_svc().get_character(character_id)
    inv_vm  = _inv_svc().get_inventory(character_id)
    items   = _inv_svc().available_items()
    return render_template(
        "characters/inventory.html",
        char=char_vm, inventory=inv_vm, items=items
    )


@bp.route("/characters/<int:character_id>/inventory/add", methods=["POST"])
def inventory_add(character_id):
    item_id  = int(request.form["ItemID"])
    quantity = int(request.form.get("Quantity", 1))
    _inv_svc().add_item(character_id, item_id, quantity)
    flash("Item added to inventory.", "success")
    return redirect(url_for("main.character_inventory", character_id=character_id))


@bp.route("/inventory/<int:inventory_id>/remove", methods=["POST"])
def inventory_remove(inventory_id):
    from repositories.repositories import InventoryRepository
    inv = InventoryRepository().get_by_id(inventory_id)
    cid = inv["CharacterID"]
    _inv_svc().remove_item(inventory_id)
    flash("Item removed.", "warning")
    return redirect(url_for("main.character_inventory", character_id=cid))


@bp.route("/characters/<int:character_id>/quests")
def character_quests(character_id):
    char_vm = _char_svc().get_character(character_id)
    cq_vm   = _qp_svc().get_character_quests(character_id)
    quests  = _qp_svc().available_quests()
    return render_template(
        "characters/quests.html",
        char=char_vm, character_quests=cq_vm, quests=quests
    )


@bp.route("/characters/<int:character_id>/quests/assign", methods=["POST"])
def quest_assign(character_id):
    quest_id = int(request.form["QuestID"])
    _qp_svc().assign_quest(character_id, quest_id)
    flash("Quest assigned.", "success")
    return redirect(url_for("main.character_quests", character_id=character_id))


@bp.route("/character-quests/<int:cq_id>/complete", methods=["POST"])
def quest_complete(cq_id):
    from repositories.repositories import CharacterQuestRepository
    cq  = CharacterQuestRepository().get_by_id(cq_id)
    cid = cq["CharacterID"]
    _qp_svc().complete_quest(cq_id)
    flash("Quest marked as complete!", "success")
    return redirect(url_for("main.character_quests", character_id=cid))


#Items

@bp.route("/items")
def item_list():
    vm = _item_svc().list_items()
    return render_template("items/list.html", vm=vm)


@bp.route("/items/new", methods=["GET", "POST"])
def item_create():
    svc = _item_svc()
    if request.method == "POST":
        data = {
            "ItemName":   request.form["ItemName"],
            "ItemTypeID": int(request.form["ItemTypeID"]),
            "RarityID":   int(request.form["RarityID"]),
        }
        svc.create_item(data)
        flash("Item created.", "success")
        return redirect(url_for("main.item_list"))
    form_vm = svc.get_form_data()
    return render_template("items/form.html", form_vm=form_vm)


@bp.route("/items/<int:item_id>/delete", methods=["POST"])
def item_delete(item_id):
    _item_svc().delete_item(item_id)
    flash("Item deleted.", "warning")
    return redirect(url_for("main.item_list"))


#Quests

@bp.route("/quests")
def quest_list():
    vm = _quest_svc().list_quests()
    return render_template("quests/list.html", vm=vm)


@bp.route("/quests/new", methods=["GET", "POST"])
def quest_create():
    svc = _quest_svc()
    if request.method == "POST":
        data = {
            "QuestName":    request.form["QuestName"],
            "RegionID":     int(request.form["RegionID"]),
            "DifficultyID": int(request.form["DifficultyID"]),
        }
        svc.create_quest(data)
        flash("Quest created.", "success")
        return redirect(url_for("main.quest_list"))
    form_vm = svc.get_form_data()
    return render_template("quests/form.html", form_vm=form_vm)


@bp.route("/quests/<int:quest_id>/delete", methods=["POST"])
def quest_delete(quest_id):
    _quest_svc().delete_quest(quest_id)
    flash("Quest deleted.", "warning")
    return redirect(url_for("main.quest_list"))


#Rewards

@bp.route("/rewards")
def reward_list():
    vm = _reward_svc().list_rewards()
    return render_template("rewards/list.html", vm=vm)


@bp.route("/rewards/new", methods=["GET", "POST"])
def reward_create():
    svc = _reward_svc()
    if request.method == "POST":
        value_raw = request.form.get("Value", "").strip()
        item_raw  = request.form.get("ItemID", "").strip()
        data = {
            "RewardName":   request.form["RewardName"],
            "RewardTypeID": int(request.form["RewardTypeID"]),
            "Value":        int(value_raw) if value_raw else None,
            "ItemID":       int(item_raw)  if item_raw  else None,
        }
        svc.create_reward(data)
        flash("Reward created.", "success")
        return redirect(url_for("main.reward_list"))
    form_vm = svc.get_form_data()
    return render_template("rewards/form.html", form_vm=form_vm)


@bp.route("/rewards/<int:reward_id>/delete", methods=["POST"])
def reward_delete(reward_id):
    _reward_svc().delete_reward(reward_id)
    flash("Reward deleted.", "warning")
    return redirect(url_for("main.reward_list"))


@bp.route("/quests/<int:quest_id>/rewards")
def quest_rewards(quest_id):
    quest_vm = QuestService().get_quest(quest_id)
    qr_vm    = _qr_svc().get_quest_rewards(quest_id)
    rewards  = _qr_svc().available_rewards()
    return render_template("quests/rewards.html", quest=quest_vm, quest_rewards=qr_vm, rewards=rewards)


@bp.route("/quests/<int:quest_id>/rewards/add", methods=["POST"])
def quest_reward_add(quest_id):
    reward_id = int(request.form["RewardID"])
    _qr_svc().add_reward(quest_id, reward_id)
    flash("Reward added to quest.", "success")
    return redirect(url_for("main.quest_rewards", quest_id=quest_id))


@bp.route("/quest-rewards/<int:qr_id>/remove", methods=["POST"])
def quest_reward_remove(qr_id):
    from repositories.repositories import QuestRewardRepository
    qr  = QuestRewardRepository().get_by_id(qr_id)
    qid = qr["QuestID"]
    _qr_svc().remove_reward(qr_id)
    flash("Reward removed.", "warning")
    return redirect(url_for("main.quest_rewards", quest_id=qid))
