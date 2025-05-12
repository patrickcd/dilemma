# Dilemma Expression Examples  
This document contains examples of using the Dilemma expression language.  
  
  
### String  
Check if two words are equal  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'hello' == 'hello'` | `True` |  
  

---
  
Check if two words are not equal  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'hello' != 'world'` | `True` |  
  

---
  
Check if a phrase contains a word  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'world' in 'hello world'` | `True` |  
  

---
  
Check if two variables are equal  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `var1 == var2` | `True` |  
  
  
#### Context  
```json
{
  "var1": "hello",
  "var2": "hello"
}
```  

---
  
Check if a filename matches a pattern with wildcard  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'document.pdf' like '*.pdf'` | `True` |  
  

---
  
Check if a string matches a pattern with ? (single character wildcard)  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'user123' like 'user???'` | `True` |  
  

---
  
Demonstrate case-insensitive matching with the &#x27;like&#x27; operator  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'Hello.TXT' like '*.txt'` | `True` |  
  

---
  
Match a variable against a pattern  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `filename like '*.jpg'` | `True` |  
  
  
#### Context  
```json
{
  "filename": "vacation-photo.JPG"
}
```  

---
  
  
### Maths  
Multiply two integers  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `8 * 8` | `64` |  
  

---
  
Divide two integers  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `64 / 8` | `8` |  
  

---
  
Add two integers  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `8 + 8` | `16` |  
  

---
  
Subtract two integers  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `8 - 8` | `0` |  
  

---
  
Multiply two floating point numbers  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `0.5 * 8.0` | `4.0` |  
  

---
  
Use variables in expressions  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `banana.price * order.quantity` | `16` |  
  
  
#### Context  
```json
{
  "banana": {
    "price": 2
  },
  "order": {
    "quantity": 8
  }
}
```  

---
  
  
### Date State  
Verify a date in the past  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `past_date is $past` | `True` |  
  
  
#### Context  
```json
{
  "past_date": "2025-05-11 13:01:53 UTC"
}
```  

---
  
Verify a date in the future  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `future_date is $future` | `True` |  
  
  
#### Context  
```json
{
  "future_date": "2025-05-13 13:01:53 UTC"
}
```  

---
  
Verify a date is $today  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `today_date is $today` | `True` |  
  
  
#### Context  
```json
{
  "today_date": "2025-05-12 13:01:53 UTC"
}
```  

---
  
  
### Time Window  
Check event within recent hours  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `recent_event within 12 hours` | `True` |  
  
  
#### Context  
```json
{
  "recent_event": "2025-05-12 12:01:53 UTC"
}
```  

---
  
Check event older than a week  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `old_event older than 1 week` | `True` |  
  
  
#### Context  
```json
{
  "old_event": "2025-05-05 13:01:53 UTC"
}
```  

---
  
Check event within minutes (not hours)  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `very_recent within 30 minutes` | `True` |  
  
  
#### Context  
```json
{
  "very_recent": "2025-05-12 13:01:53 UTC"
}
```  

---
  
  
### Date Comparison  
Compare two dates with before  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `start_date before end_date` | `True` |  
  
  
#### Context  
```json
{
  "start_date": "2025-05-11 13:01:53 UTC",
  "end_date": "2025-05-13 13:01:53 UTC"
}
```  

---
  
Compare two dates with after  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `end_date after start_date` | `True` |  
  
  
#### Context  
```json
{
  "start_date": "2025-05-11 13:01:53 UTC",
  "end_date": "2025-05-13 13:01:53 UTC"
}
```  

---
  
Check same day (should be true)  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `same_day_morning same_day_as same_day_evening` | `True` |  
  
  
#### Context  
```json
{
  "same_day_morning": "2023-05-10T08:00:00Z",
  "same_day_evening": "2023-05-10T20:00:00Z"
}
```  

---
  
Check same day (should be false)  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `different_days same_day_as other_day` | `False` |  
  
  
#### Context  
```json
{
  "different_days": "2023-05-10T08:00:00Z",
  "other_day": "2023-05-11T08:00:00Z"
}
```  

---
  
  
### Complex  
Check if project is currently active  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `project_start is $past and project_end is $future` | `True` |  
  
  
#### Context  
```json
{
  "project_start": "2025-05-11 13:01:53 UTC",
  "project_end": "2025-05-13 13:01:53 UTC"
}
```  

---
  
Recent login but account not new  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `last_login within 4 hours and signup_date older than 1 day` | `True` |  
  
  
#### Context  
```json
{
  "last_login": "2025-05-12 12:01:53 UTC",
  "signup_date": "2025-05-11 13:01:53 UTC"
}
```  

---
  
  
### String Dates  
Compare ISO formatted date string  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `iso_date before '2030-01-01'` | `True` |  
  
  
#### Context  
```json
{
  "iso_date": "2023-05-10T00:00:00Z"
}
```  

---
  
Check literal date is $past  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'2020-01-01' is $past` | `True` |  
  

---
  
Check literal date older than period  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'2020-01-01' older than 1 year` | `True` |  
  

---
  
  
### Time Units  
Use hours time unit  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `hour_ago within 2 hours` | `True` |  
  
  
#### Context  
```json
{
  "hour_ago": "2025-05-12 12:01:53 UTC"
}
```  

---
  
Use minutes time unit  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `hour_ago within 120 minutes` | `True` |  
  
  
#### Context  
```json
{
  "hour_ago": "2025-05-12 12:01:53 UTC"
}
```  

---
  
Use days time unit  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `week_ago older than 6 days` | `True` |  
  
  
#### Context  
```json
{
  "week_ago": "2025-05-05 13:01:53 UTC"
}
```  

---
  
  
### List Operations  
Check if an element exists in a list using &#x27;in&#x27;  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'admin' in user.roles` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "roles": [
      "user",
      "admin",
      "editor"
    ],
    "name": "John Doe"
  }
}
```  

---
  
Use a variable as the item to check in a list  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `requested_role in available_roles` | `True` |  
  
  
#### Context  
```json
{
  "requested_role": "manager",
  "available_roles": [
    "user",
    "admin",
    "manager",
    "guest"
  ]
}
```  

---
  
Alternative contains syntax for list membership  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `permissions contains 'delete'` | `True` |  
  
  
#### Context  
```json
{
  "permissions": [
    "read",
    "write",
    "delete",
    "share"
  ]
}
```  

---
  
Check behavior when element is not in list  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'superadmin' in user.roles` | `False` |  
  
  
#### Context  
```json
{
  "user": {
    "roles": [
      "user",
      "admin",
      "editor"
    ]
  }
}
```  

---
  
  
### Object Operations  
Check if a key exists in a dictionary  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'address' in user.profile` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "profile": {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "address": "123 Main St",
      "phone": "555-1234"
    }
  }
}
```  

---
  
Use a variable to check dictionary key membership  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `required_field in form_data` | `False` |  
  
  
#### Context  
```json
{
  "required_field": "tax_id",
  "form_data": {
    "name": "Company Inc",
    "email": "info@company.com",
    "address": "456 Business Ave"
  }
}
```  

---
  
Use contains operator with dictionary  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `config contains 'debug_mode'` | `True` |  
  
  
#### Context  
```json
{
  "config": {
    "app_name": "MyApp",
    "version": "1.2.3",
    "debug_mode": true,
    "theme": "dark"
  }
}
```  

---
  
  
### Mixed Collections  
Check membership in a list nested within a dictionary  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'python' in user.skills.programming` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "name": "Alex Developer",
    "skills": {
      "programming": [
        "javascript",
        "python",
        "go"
      ],
      "languages": [
        "english",
        "spanish"
      ]
    }
  }
}
```  

---
  
Combine collection operators with other logical operators  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'admin' in user.roles and user.settings contains 'notifications' and user.settings.notifications` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "roles": [
      "user",
      "admin"
    ],
    "settings": {
      "theme": "light",
      "notifications": true,
      "privacy": "high"
    }
  }
}
```  

---
  
  
### Collection Equality  
Compare two lists for equality  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `user.permissions == required_permissions` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "permissions": [
      "read",
      "write",
      "delete"
    ]
  },
  "required_permissions": [
    "read",
    "write",
    "delete"
  ]
}
```  

---
  
Compare two dictionaries for equality  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `user.preferences == default_preferences` | `False` |  
  
  
#### Context  
```json
{
  "user": {
    "preferences": {
      "theme": "dark",
      "font_size": "medium"
    }
  },
  "default_preferences": {
    "theme": "light",
    "font_size": "medium"
  }
}
```  

---
  
  
### Complex Scenarios  
Use membership test with a composite condition  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `(user.role in admin_roles) or (user.domain in approved_domains and user.verified)` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "role": "manager",
    "email": "user@company.com",
    "domain": "company.com",
    "verified": true
  },
  "admin_roles": [
    "admin",
    "superadmin"
  ],
  "approved_domains": [
    "company.com",
    "partner.org"
  ]
}
```  

---
  
  
### Path Syntax  
Look up elements in arrays using indexing  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `teams[0].name == 'Frontend'` | `True` |  
  
  
#### Context  
```json
{
  "teams": [
    {
      "name": "Frontend",
      "members": [
        "Alice",
        "Bob"
      ]
    },
    {
      "name": "Backend",
      "members": [
        "Charlie",
        "Dave"
      ]
    }
  ]
}
```  

---
  
Use nested array indexing in paths  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `departments[0].teams[1].name == 'Backend'` | `True` |  
  
  
#### Context  
```json
{
  "departments": [
    {
      "name": "Engineering",
      "teams": [
        {
          "name": "Frontend",
          "members": [
            "Alice",
            "Bob"
          ]
        },
        {
          "name": "Backend",
          "members": [
            "Charlie",
            "Dave"
          ]
        }
      ]
    },
    {
      "name": "Marketing",
      "teams": [
        {
          "name": "Digital",
          "members": [
            "Eve",
            "Frank"
          ]
        }
      ]
    }
  ]
}
```  

---
  
Test property of an element accessed through indexing  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `users[1].role == 'admin' and users[1].verified` | `True` |  
  
  
#### Context  
```json
{
  "users": [
    {
      "username": "johndoe",
      "role": "user",
      "verified": false
    },
    {
      "username": "janedoe",
      "role": "admin",
      "verified": true
    }
  ]
}
```  

---
  
Combine array indexing with membership test  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `'testing' in projects[0].tags and projects[1].status == 'completed'` | `True` |  
  
  
#### Context  
```json
{
  "projects": [
    {
      "name": "Feature A",
      "tags": [
        "important",
        "testing",
        "frontend"
      ],
      "status": "in_progress"
    },
    {
      "name": "Feature B",
      "tags": [
        "backend",
        "documentation"
      ],
      "status": "completed"
    }
  ]
}
```  

---
  
  
### Complex Path Operations  
Complex expression combining array lookups with object properties  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `organization.departments[0].teams[0].members[1] == 'Bob' and organization.departments[1].teams[0].members[0] == 'Eve'` | `True` |  
  
  
#### Context  
```json
{
  "organization": {
    "name": "Acme Corp",
    "departments": [
      {
        "name": "Engineering",
        "teams": [
          {
            "name": "Frontend",
            "members": [
              "Alice",
              "Bob"
            ]
          },
          {
            "name": "Backend",
            "members": [
              "Charlie",
              "Dave"
            ]
          }
        ]
      },
      {
        "name": "Marketing",
        "teams": [
          {
            "name": "Digital",
            "members": [
              "Eve",
              "Frank"
            ]
          }
        ]
      }
    ]
  }
}
```  

---
  
  
### Container Operations  
Check if containers are empty using &#x27;is $empty&#x27;  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `ghost_crew is $empty and deserted_mansion is $empty and (treasure_chest is $empty) == false` | `True` |  
  
  
#### Context  
```json
{
  "ghost_crew": [],
  "treasure_chest": [
    "ancient coin",
    "golden chalice",
    "ruby necklace"
  ],
  "deserted_mansion": {},
  "dragon_hoard": {
    "golden_crown": 1500,
    "enchanted_sword": 3000,
    "crystal_orb": 750
  }
}
```  

---
  
  
### Nested Objects  
Check if user is eligible for premium features  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `user.account.is_active and (user.subscription.level == 'premium' or user.account.credits > 100)` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "account": {
      "is_active": true,
      "credits": 150,
      "created_at": "2025-05-05 13:01:53 UTC"
    },
    "subscription": {
      "level": "basic",
      "renewal_date": "2025-06-11 13:01:53 UTC"
    }
  }
}
```  

---
  
Evaluate complex project status conditions  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `project.status == 'in_progress' and (project.metrics.completion > 50 or (project.team.size >= 3 and project.priority == 'high'))` | `True` |  
  
  
#### Context  
```json
{
  "project": {
    "status": "in_progress",
    "start_date": "2025-05-05 13:01:53 UTC",
    "deadline": "2025-06-11 13:01:53 UTC",
    "metrics": {
      "completion": 45,
      "quality": 98
    },
    "team": {
      "size": 5,
      "lead": "Alice"
    },
    "priority": "high"
  }
}
```  

---
  
  
### Mixed Date Logic  
Check if order is eligible for express shipping  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `order.status == 'confirmed' and order.created_at within 24 hours and (order.items.count < 5 or (order.customer.tier == 'gold' and order.total_value > 100))` | `True` |  
  
  
#### Context  
```json
{
  "order": {
    "status": "confirmed",
    "created_at": "2025-05-12 12:01:53 UTC",
    "items": {
      "count": 7,
      "categories": [
        "electronics",
        "books"
      ]
    },
    "customer": {
      "tier": "gold",
      "since": "2025-05-05 13:01:53 UTC"
    },
    "total_value": 250
  }
}
```  

---
  
Multiple date conditions with nested properties  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `(user.last_login within 7 days or user.auto_login) and (user.account.trial_ends is $future or user.account.subscription.status == 'active')` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "last_login": "2025-05-05 13:01:53 UTC",
    "auto_login": true,
    "registration_date": "2023-01-15",
    "account": {
      "trial_ends": "2025-05-11 13:01:53 UTC",
      "subscription": {
        "status": "active",
        "plan": "premium",
        "next_payment": "2025-06-11 13:01:53 UTC"
      }
    }
  }
}
```  

---
  
  
### Complex Precedence  
Test operator precedence with mixed conditions  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `user.settings.notifications.enabled and (user.last_seen older than 1 day or user.preferences.urgent_only) and ('admin' in user.roles or user.tasks.pending > 0)` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "settings": {
      "notifications": {
        "enabled": true,
        "channels": [
          "email",
          "push"
        ]
      },
      "theme": "dark"
    },
    "last_seen": "2025-05-05 13:01:53 UTC",
    "preferences": {
      "urgent_only": false,
      "language": "en"
    },
    "roles": "user, admin",
    "tasks": {
      "pending": 3,
      "completed": 27
    }
  }
}
```  

---
  
  
### Jq Basics  
Basic JQ expression to access a nested property  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.user.profile.name` == 'Alice'` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "profile": {
      "name": "Alice",
      "age": 32
    },
    "settings": {
      "notifications": true
    }
  }
}
```  

---
  
  
### Jq Arrays  
Access elements in an array using JQ indexing  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.team[1].role` == 'developer'` | `True` |  
  
  
#### Context  
```json
{
  "team": [
    {
      "name": "Bob",
      "role": "manager"
    },
    {
      "name": "Charlie",
      "role": "developer"
    },
    {
      "name": "Diana",
      "role": "designer"
    }
  ]
}
```  

---
  
Check array length using JQ pipe function  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.products | length` > 2` | `True` |  
  
  
#### Context  
```json
{
  "products": [
    {
      "id": 101,
      "name": "Laptop"
    },
    {
      "id": 102,
      "name": "Phone"
    },
    {
      "id": 103,
      "name": "Tablet"
    }
  ]
}
```  

---
  
Check if any array element matches a condition  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.users[] | select(.role == "admin") | .name` == 'Eva'` | `True` |  
  
  
#### Context  
```json
{
  "users": [
    {
      "name": "Dave",
      "role": "user"
    },
    {
      "name": "Eva",
      "role": "admin"
    },
    {
      "name": "Frank",
      "role": "user"
    }
  ]
}
```  

---
  
  
### Jq Filtering  
Filter array elements based on a condition  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.orders[] | select(.status == "completed") | .id` == 1003` | `True` |  
  
  
#### Context  
```json
{
  "orders": [
    {
      "id": 1001,
      "status": "pending"
    },
    {
      "id": 1002,
      "status": "processing"
    },
    {
      "id": 1003,
      "status": "completed"
    }
  ]
}
```  

---
  
  
### Jq Mixed  
Combine JQ with regular Dilemma expressions  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.user.membership.level` == 'gold' and user.account.active == true` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "membership": {
      "level": "gold",
      "since": "2025-05-05 13:01:53 UTC"
    },
    "account": {
      "active": true,
      "credits": 500
    }
  }
}
```  

---
  
  
### Jq Advanced  
Complex data transformation with JQ  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.departments[] | select(.name == "Engineering").employees | map(.salary) | add / length` > 75000` | `True` |  
  
  
#### Context  
```json
{
  "departments": [
    {
      "name": "Marketing",
      "employees": [
        {
          "name": "Grace",
          "salary": 65000
        },
        {
          "name": "Henry",
          "salary": 68000
        }
      ]
    },
    {
      "name": "Engineering",
      "employees": [
        {
          "name": "Isla",
          "salary": 78000
        },
        {
          "name": "Jack",
          "salary": 82000
        },
        {
          "name": "Kate",
          "salary": 80000
        }
      ]
    }
  ]
}
```  

---
  
Check if an array contains a specific value  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.user.permissions | contains(["edit"])`` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "id": 1234,
    "name": "Lucy",
    "permissions": [
      "read",
      "edit",
      "share"
    ]
  }
}
```  

---
  
Use JQ to conditionally create and check an object  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``if .user.premium then {access: "full"} else {access: "limited"} end | .access` == 'full'` | `True` |  
  
  
#### Context  
```json
{
  "user": {
    "premium": true,
    "account_type": "business"
  }
}
```  

---
  
Complex JQ expression with deeply nested parentheses and operations  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.employees | map( ((.performance.rating * 0.5) + ((.projects | map(select(.status == "completed") | .difficulty) | add // 0) * 0.3) + (if (.years_experience > 5) then ((.leadership_score // 0) * 0.2) else ((.learning_speed // 0) * 0.2) end) ) * (if .department == "Engineering" then 1.1 else 1 end) ) | add / length` > 75` | `True` |  
  
  
#### Context  
```json
{
  "employees": [
    {
      "name": "Alice",
      "department": "Engineering",
      "performance": {
        "rating": 98
      },
      "projects": [
        {
          "name": "Project A",
          "status": "completed",
          "difficulty": 9
        },
        {
          "name": "Project B",
          "status": "completed",
          "difficulty": 10
        }
      ],
      "years_experience": 7,
      "leadership_score": 95
    },
    {
      "name": "Bob",
      "department": "Engineering",
      "performance": {
        "rating": 95
      },
      "projects": [
        {
          "name": "Project C",
          "status": "completed",
          "difficulty": 8
        },
        {
          "name": "Project D",
          "status": "in_progress",
          "difficulty": 10
        }
      ],
      "years_experience": 4,
      "learning_speed": 98
    },
    {
      "name": "Charlie",
      "department": "Marketing",
      "performance": {
        "rating": 98
      },
      "projects": [
        {
          "name": "Project E",
          "status": "completed",
          "difficulty": 10
        },
        {
          "name": "Project F",
          "status": "completed",
          "difficulty": 8
        }
      ],
      "years_experience": 6,
      "leadership_score": 90
    }
  ]
}
```  

---
  
  
### Jq With Dates  
Use JQ to extract a date for comparison  
  
| Expression | Expected Result |  
|:---:|:---:|  
| ``.project.milestones[] | select(.name == "beta").date` is $past` | `True` |  
  
  
#### Context  
```json
{
  "project": {
    "name": "Product Launch",
    "milestones": [
      {
        "name": "alpha",
        "date": "2025-06-11 13:01:53 UTC"
      },
      {
        "name": "beta",
        "date": "2025-05-11 13:01:53 UTC"
      },
      {
        "name": "release",
        "date": "2025-05-12 15:01:53 UTC"
      }
    ]
  }
}
```  

---
  
  
### Jq Parsing  
Simple JQ expression nested inside multiple levels of Dilemma parentheses  
  
| Expression | Expected Result |  
|:---:|:---:|  
| `(5 + ((`.users | length` * 2) - 1)) > 5` | `True` |  
  
  
#### Context  
```json
{
  "users": [
    {
      "id": 1,
      "name": "Alice"
    },
    {
      "id": 2,
      "name": "Bob"
    },
    {
      "id": 3,
      "name": "Charlie"
    }
  ]
}
```  

---
  
