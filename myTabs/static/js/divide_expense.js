window.onload = function () {
  var element = document.getElementById("id_data");
  var tabUsers = JSON.parse(element.getAttribute("data-tab-users"));

  var btn1 = document.getElementById("equally-btn");
  var btn2 = document.getElementById("advanced-btn");

  btn1.onclick = disable_inputs;
  btn2.onclick = enable_inputs;

  let timeout;

  let cost = document.getElementById("id_cost");
  for (let i = 0; i < tabUsers.length; i++) {
    console.log(tabUsers[i].id);
  }
  function enable_inputs() {
    divideCostAdvaced();
    document.getElementById("cost_left").style.display = "block";
    for (let i = 0; i < tabUsers.length; i++) {
      document
        .getElementById("cost_" + tabUsers[i].id)
        .removeAttribute("readonly");
    }
  }

  function disable_inputs() {
    document.getElementById("cost_left").style.display = "none";
    for (let i = 0; i < tabUsers.length; i++) {
      document
        .getElementById("cost_" + tabUsers[i].id)
        .setAttribute("readonly", true);
    }
    divideCostEqually();
  }

  if (cost) {
    cost.addEventListener("input", () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => divideCostEqually(), 100);
    });
  }

  let user_costs = [];
  for (let i = 0; i < tabUsers.length; i++) {
    user_costs.push(document.getElementById("cost_" + tabUsers[i].id));
  }
  console.log(user_costs);

  for (let i = 0; i < tabUsers.length; i++) {
    document
      .getElementById("check_" + tabUsers[i].id)
      .addEventListener("click", () => {
        var checkbox = document.getElementById("check_" + tabUsers[i].id);
        var cost = document.getElementById("cost" + tabUsers[i].id);
        if (checkbox.checked == false) {
          checkbox.style.backgroundColor = "var(--white)";
          checkbox.style.borderColor = "var(--gray)";
        } else {
          checkbox.style.backgroundColor = "var(--tertiary)";
          checkbox.style.borderColor = "var(--tertiary)";
        }
        if (btn1.checked) {
          clearTimeout(timeout);
          timeout = setTimeout(divideCostEqually, 100);
        } else {
          clearTimeout(timeout);
          timeout = setTimeout(divideCostAdvaced, 100);
        }
      });
    document
      .getElementById("cost_" + tabUsers[i].id)
      .addEventListener("change", (event) => {
        if (btn1.checked) {
          clearTimeout(timeout);
          timeout = setTimeout(divideCostEqually, 100);
        } else {
          console.log(event.target.value);
          cost = event.target.value;
          if (cost == "" || cost < 0) {
            cost = 0;
          }
          var cost = parseFloat(cost);
          var cost = cost.toFixed(2);

          console.log(cost);
          event.target.value = cost;
          clearTimeout(timeout);
          timeout = setTimeout(divideCostAdvaced, 100);
        }
      });
  }

  function divideCostEqually() {
    if (cost.value >= 0) {
      let total = cost.value;
      let checked_users_costs = getCheckedUsersCost();
      let nb_users = checked_users_costs.length;
      let cost_per_user = (total / nb_users).toFixed(2);
      let cost_per_user_rest = total - cost_per_user * nb_users;
      console.log("cost: " + cost_per_user_rest);
      for (let i = 0; i < nb_users; i++) {
        checked_users_costs[i].value = cost_per_user;
      }
    }
  }

  function divideCostAdvaced() {
    let total = cost.value;
    let checked_users_costs = getCheckedUsersCost();
    let nb_users = checked_users_costs.length;
    let current_sum = 0;

    for (let i = 0; i < nb_users; i++) {
      current_sum += parseFloat(checked_users_costs[i].value);
    }

    let cost_left = total - current_sum;
    cost_left = cost_left.toFixed(2);
    if (cost_left < 0) {
      document.getElementById("cost_left").style.color = "green";
      document.getElementById("cost_left").innerHTML =
        "Surplus of " + -1 * cost_left + "zł";
    } else if (cost_left == 0) {
      document.getElementById("cost_left").style.color = "black";
      document.getElementById("cost_left").innerHTML = "Costs are equal";
    } else {
      document.getElementById("cost_left").style.color = "red";
      document.getElementById("cost_left").innerHTML =
        "Shortage of " + cost_left + "zł";
    }
  }

  function getCheckedUsersCost() {
    let checked_users = [];
    for (let i = 0; i < tabUsers.length; i++) {
      if (document.getElementById("check_" + tabUsers[i].id).checked) {
        checked_users.push(document.getElementById("cost_" + tabUsers[i].id));
        if (btn1.checked) {
          document
            .getElementById("cost_" + tabUsers[i].id)
            .setAttribute("readonly", true);
        } else {
          document
            .getElementById("cost_" + tabUsers[i].id)
            .removeAttribute("readonly");
        }
      } else {
        document.getElementById("cost_" + tabUsers[i].id).value = "0.00";
        document
          .getElementById("cost_" + tabUsers[i].id)
          .setAttribute("readonly", true);
      }
    }
    return checked_users;
  }
};
