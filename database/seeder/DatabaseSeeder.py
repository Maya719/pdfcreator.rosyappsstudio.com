from database.seeder.UserSeeder import UserSeeder


class DatabaseSeeder:
    def run(self):
        results = []
        results.append(UserSeeder().run())
        return results
